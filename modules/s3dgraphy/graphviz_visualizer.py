#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Graphviz visualizer for S3DGraphy Extended Matrix
Uses the existing Graphviz installation from PyArchInit
"""

import os
import subprocess
import tempfile
from typing import Dict, List, Optional
import platform


class GraphvizVisualizer:
    """
    Creates a hierarchical graph visualization using Graphviz
    """

    def __init__(self):
        self.dot_content = []
        self.levels = {}

    def create_graph_image(self, graph_data: Dict, output_path: str) -> bool:
        """
        Create a hierarchical graph visualization using Graphviz

        Args:
            graph_data: Extended Matrix data
            output_path: Path to save the image

        Returns:
            True if successful
        """
        try:
            # Create DOT file content
            self._create_dot_content(graph_data)

            # Write DOT file
            dot_path = output_path.replace('.png', '.dot')
            with open(dot_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(self.dot_content))

            # Get Graphviz path based on platform
            dot_executable = self._get_graphviz_path()

            if not dot_executable:
                print("Graphviz not found in standard locations")
                return False

            # Generate PNG from DOT
            print(f"Running Graphviz: {dot_executable}")
            cmd = [dot_executable, '-Tpng', dot_path, '-o', output_path]

            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode == 0:
                print(f"✅ Graph image created: {output_path}")
                # Keep DOT file for debugging (can be removed later)
                print(f"DOT file saved: {dot_path}")
                return True
            else:
                print(f"❌ Graphviz error: {result.stderr}")
                return False

        except Exception as e:
            print(f"Error creating graph with Graphviz: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

    def _get_graphviz_path(self) -> Optional[str]:
        """
        Get the path to Graphviz executable
        PyArchInit already has this configured
        """
        system = platform.system()

        if system == 'Darwin':  # macOS
            # Common locations on macOS
            paths = [
                '/opt/homebrew/bin/dot',  # M1 Macs with Homebrew
                '/usr/local/bin/dot',      # Intel Macs with Homebrew
                '/opt/local/bin/dot',      # MacPorts
                '/usr/bin/dot'             # System
            ]
        elif system == 'Windows':
            paths = [
                r'C:\Program Files\Graphviz\bin\dot.exe',
                r'C:\Program Files (x86)\Graphviz\bin\dot.exe',
                r'C:\Graphviz\bin\dot.exe'
            ]
        else:  # Linux
            paths = [
                '/usr/bin/dot',
                '/usr/local/bin/dot'
            ]

        # Check which path exists
        for path in paths:
            if os.path.exists(path):
                return path

        # Try to find dot in PATH
        try:
            result = subprocess.run(['which', 'dot'], capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout.strip()
        except:
            pass

        return None

    def _create_dot_content(self, graph_data: Dict):
        """
        Create Graphviz DOT file content
        """
        self.dot_content = []

        # Start digraph
        self.dot_content.append('digraph ExtendedMatrix {')
        self.dot_content.append('  rankdir=TB;')  # Top to bottom
        self.dot_content.append('  node [shape=box, style="filled,rounded", fontname="Arial", width=2, height=0.8];')
        self.dot_content.append('  edge [fontname="Arial", fontsize=10];')
        self.dot_content.append('  bgcolor="white";')
        self.dot_content.append('  ranksep=1.0;')  # Increase vertical spacing
        self.dot_content.append('  nodesep=0.5;')  # Horizontal spacing
        self.dot_content.append('')

        # Calculate levels for hierarchical layout
        self._calculate_levels(graph_data)

        # Debug: print levels
        print(f"Calculated levels for {len(self.levels)} nodes:")
        for node_id, level in sorted(self.levels.items(), key=lambda x: x[1]):
            print(f"  {node_id}: Level {level}")

        # Group nodes by level for ranking
        level_nodes = {}
        for node in graph_data.get('nodes', []):
            node_id = node.get('node_id', '')
            if node.get('node_type') == 'geo_position':
                continue

            level = self.levels.get(node_id, 0)
            if level not in level_nodes:
                level_nodes[level] = []
            level_nodes[level].append(node)

        print(f"Nodes grouped into {len(level_nodes)} levels")

        # Add nodes grouped by level with rank constraints
        self.dot_content.append('  // Nodes by level')
        for level in sorted(level_nodes.keys()):
            if level_nodes[level]:
                self.dot_content.append(f'  // Level {level}')
                self.dot_content.append('  {')
                self.dot_content.append('    rank=same;')

                for node in level_nodes[level]:
                    node_id = node.get('node_id', '')
                    label = node.get('name', node.get('us', ''))
                    unita_tipo = node.get('unita_tipo', 'US')
                    description = node.get('description', '')

                    # Clean label
                    if label:
                        label = label.replace('"', '\\"')
                    if description:
                        description = description.replace('"', '\\"')[:40]
                        full_label = f"{label}\\n{description}"
                    else:
                        full_label = label

                    # Color based on unit type
                    color_map = {
                        'US': '#90EE90',  # Light green
                        'USM': '#FFD700',  # Gold
                        'USF': '#87CEEB',  # Sky blue
                        'USD': '#DEB887',  # Burlywood
                        'USR': '#DDA0DD',  # Plum
                        'CON': '#FFA07A',  # Light salmon
                        'SF': '#F0E68C',   # Khaki
                        'virtual_reconstruction': '#FFB6C1'  # Light pink
                    }
                    color = color_map.get(unita_tipo, '#E0E0E0')

                    # Add node
                    self.dot_content.append(f'    "{node_id}" [label="{full_label}", '
                                          f'fillcolor="{color}", color="black", '
                                          f'fontcolor="black", penwidth=2];')

                self.dot_content.append('  }')

        self.dot_content.append('')

        # Add edges (relationships)
        self.dot_content.append('  // Relationships')
        edge_count = 0
        edges = graph_data.get('edges', [])
        print(f"Processing {len(edges)} edges...")

        for edge in edges:
            source = edge.get('edge_source', '')
            target = edge.get('edge_target', '')
            edge_type = edge.get('edge_type', '')

            # Skip invalid edges
            if not source or not target:
                print(f"  Skipping edge with missing source or target")
                continue

            if source not in self.levels:
                print(f"  Warning: source {source} not in levels")
            if target not in self.levels:
                print(f"  Warning: target {target} not in levels")

            # Style based on edge type
            if edge_type == 'is_before':
                style = 'solid'
                color = 'blue'
                label = ''
                penwidth = '2'
            elif edge_type == 'has_same_time':
                style = 'dashed'
                color = 'green'
                label = 'contemp.'
                penwidth = '2'
            else:
                style = 'dotted'
                color = 'gray'
                label = edge_type[:10] if edge_type else ''
                penwidth = '1'

            # Add edge
            self.dot_content.append(f'  "{source}" -> "{target}" '
                                  f'[style={style}, color={color}, label="{label}", penwidth={penwidth}];')
            edge_count += 1

        print(f"Added {edge_count} edges to graph")

        # Add legend
        self.dot_content.append('')
        self.dot_content.append('  // Legend')
        self.dot_content.append('  subgraph cluster_legend {')
        self.dot_content.append('    label="Legend";')
        self.dot_content.append('    style=filled;')
        self.dot_content.append('    color=lightgray;')
        self.dot_content.append('    node [shape=box, style=filled];')
        self.dot_content.append('')
        self.dot_content.append('    "US Type" [fillcolor="#90EE90", label="US\\nStratigraphic Unit"];')
        self.dot_content.append('    "USM Type" [fillcolor="#FFD700", label="USM\\nMasonry Unit"];')
        self.dot_content.append('    "USF Type" [fillcolor="#87CEEB", label="USF\\nFeature Unit"];')
        self.dot_content.append('  }')

        # Close digraph
        self.dot_content.append('}')

    def _calculate_levels(self, graph_data: Dict):
        """
        Calculate hierarchy levels based on relationships
        Following stratigraphic principles: earlier (above) units have lower levels
        """
        # Initialize all nodes at level 0
        for node in graph_data.get('nodes', []):
            node_id = node.get('node_id', '')
            if node.get('node_type') != 'geo_position':
                self.levels[node_id] = 0

        # Build adjacency lists for topological sorting
        edges = graph_data.get('edges', [])
        predecessors = {}  # Nodes that come before each node
        successors = {}    # Nodes that come after each node

        for node in graph_data.get('nodes', []):
            node_id = node.get('node_id', '')
            if node.get('node_type') != 'geo_position':
                predecessors[node_id] = []
                successors[node_id] = []

        # Process edges
        for edge in edges:
            source = edge.get('edge_source', '')
            target = edge.get('edge_target', '')
            edge_type = edge.get('edge_type', '')

            if edge_type == 'is_before':
                # Source is stratigraphically before (above) target
                # In our visualization, source should be at a lower level (higher up)
                if source in successors and target in predecessors:
                    successors[source].append(target)
                    predecessors[target].append(source)

        # Calculate levels using topological approach
        changed = True
        iterations = 0
        max_iterations = 100

        while changed and iterations < max_iterations:
            changed = False
            iterations += 1

            for node_id in self.levels:
                # For each predecessor, this node should be at least one level below
                for pred in predecessors.get(node_id, []):
                    new_level = self.levels[pred] + 1
                    if self.levels[node_id] < new_level:
                        self.levels[node_id] = new_level
                        changed = True