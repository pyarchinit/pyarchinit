use pyo3::prelude::*;
use pyo3::types::PyDict;
use petgraph::graph::{DiGraph, NodeIndex};
use std::collections::HashMap;

/// Sugiyama-style layered graph layout for Harris Matrix visualization.
///
/// Implements the four phases of the Sugiyama algorithm:
/// 1. Layer assignment (longest-path + optional phase grouping)
/// 2. Dummy node insertion for multi-layer edges
/// 3. Crossing minimization (barycenter heuristic)
/// 4. Coordinate assignment (median positioning)
///
/// Returns a Python dict with `node_positions` and `edge_paths`.
#[pyfunction]
#[pyo3(signature = (edges, node_labels, phase_groups=None, layer_spacing=80.0, node_spacing=60.0, crossing_iterations=6))]
fn harris_matrix_layout(
    py: Python<'_>,
    edges: Vec<(String, String)>,
    node_labels: Vec<String>,
    phase_groups: Option<Vec<(String, Vec<String>)>>,
    layer_spacing: f64,
    node_spacing: f64,
    crossing_iterations: usize,
) -> PyResult<PyObject> {
    // --- Build petgraph DiGraph ---
    let mut graph = DiGraph::<String, ()>::new();
    let mut node_map: HashMap<String, NodeIndex> = HashMap::new();

    // Insert all labelled nodes first
    for label in &node_labels {
        let idx = graph.add_node(label.clone());
        node_map.insert(label.clone(), idx);
    }
    // Insert nodes that appear in edges but not in labels
    for (a, b) in &edges {
        if !node_map.contains_key(a) {
            let idx = graph.add_node(a.clone());
            node_map.insert(a.clone(), idx);
        }
        if !node_map.contains_key(b) {
            let idx = graph.add_node(b.clone());
            node_map.insert(b.clone(), idx);
        }
    }
    // Add edges
    for (a, b) in &edges {
        let a_idx = node_map[a];
        let b_idx = node_map[b];
        graph.add_edge(a_idx, b_idx, ());
    }

    let n = graph.node_count();
    if n == 0 {
        let dict = PyDict::new_bound(py);
        let empty_pos: Vec<(String, f64, f64)> = Vec::new();
        let empty_edges: Vec<(String, String, Vec<(f64, f64)>)> = Vec::new();
        dict.set_item("node_positions", empty_pos)?;
        dict.set_item("edge_paths", empty_edges)?;
        return Ok(dict.into());
    }

    // --- Phase 1: Layer assignment (longest-path from sinks, top-down) ---
    let idx_to_label: HashMap<NodeIndex, String> = node_map
        .iter()
        .map(|(k, &v)| (v, k.clone()))
        .collect();

    let mut layer_of: HashMap<NodeIndex, usize> = HashMap::new();
    assign_layers_longest_path(&graph, &mut layer_of);

    // If phase_groups provided, constrain nodes within the same phase to the same layer
    if let Some(ref groups) = phase_groups {
        apply_phase_constraints(&mut layer_of, groups, &node_map);
    }

    // Collect layers: layer_index -> Vec<NodeIndex>
    let max_layer = layer_of.values().copied().max().unwrap_or(0);
    let mut layers: Vec<Vec<NodeIndex>> = vec![Vec::new(); max_layer + 1];
    for (&node, &layer) in &layer_of {
        layers[layer].push(node);
    }
    // Sort each layer for deterministic initial ordering
    for layer in &mut layers {
        layer.sort_by(|a, b| {
            let la = idx_to_label.get(a).map(|s| s.as_str()).unwrap_or("");
            let lb = idx_to_label.get(b).map(|s| s.as_str()).unwrap_or("");
            la.cmp(lb)
        });
    }

    // --- Phase 2: Dummy node insertion ---
    // We track dummy nodes as virtual entries (not in the petgraph)
    // DummyInfo: for each long edge, list of dummy node ids per intermediate layer
    let mut dummy_counter: usize = 0;
    // Map from dummy id -> (layer, position_in_layer) — filled during ordering
    struct DummyNode {
        id: String,
        layer: usize,
    }
    let mut dummy_nodes: Vec<DummyNode> = Vec::new();
    // Expanded edge representation: original edge -> sequence of (node_id, node_id) segments
    struct ExpandedEdge {
        from_label: String,
        to_label: String,
        segments: Vec<(String, String)>, // chain of node ids including dummies
    }
    let mut expanded_edges: Vec<ExpandedEdge> = Vec::new();

    for (a_label, b_label) in &edges {
        let a_idx = node_map[a_label];
        let b_idx = node_map[b_label];
        let a_layer = layer_of[&a_idx];
        let b_layer = layer_of[&b_idx];

        if a_layer >= b_layer {
            // Same layer or upward edge (skip dummy insertion for these)
            // Still record a direct segment for routing
            expanded_edges.push(ExpandedEdge {
                from_label: a_label.clone(),
                to_label: b_label.clone(),
                segments: vec![(a_label.clone(), b_label.clone())],
            });
            continue;
        }

        let span = b_layer - a_layer;
        if span <= 1 {
            // Adjacent layers, no dummy needed
            expanded_edges.push(ExpandedEdge {
                from_label: a_label.clone(),
                to_label: b_label.clone(),
                segments: vec![(a_label.clone(), b_label.clone())],
            });
        } else {
            // Insert (span - 1) dummy nodes
            let mut chain: Vec<String> = vec![a_label.clone()];
            for k in 1..span {
                let dummy_id = format!("__dummy_{}_{}", dummy_counter, k);
                dummy_counter += 1;
                let layer = a_layer + k;
                dummy_nodes.push(DummyNode {
                    id: dummy_id.clone(),
                    layer,
                });
                layers[layer].push(NodeIndex::new(0)); // placeholder, will be tracked by name
                chain.push(dummy_id);
            }
            chain.push(b_label.clone());

            let mut segments = Vec::new();
            for w in chain.windows(2) {
                segments.push((w[0].clone(), w[1].clone()));
            }
            expanded_edges.push(ExpandedEdge {
                from_label: a_label.clone(),
                to_label: b_label.clone(),
                segments,
            });
        }
    }

    // Build unified ordering per layer: real nodes + dummy nodes
    // We need a string-based layer structure for crossing minimization
    let mut layer_order: Vec<Vec<String>> = Vec::new();
    for (li, layer) in layers.iter().enumerate() {
        let mut names: Vec<String> = Vec::new();
        for &nidx in layer {
            if let Some(label) = idx_to_label.get(&nidx) {
                if !names.contains(label) {
                    names.push(label.clone());
                }
            }
        }
        // Add dummy nodes for this layer
        for dn in &dummy_nodes {
            if dn.layer == li {
                names.push(dn.id.clone());
            }
        }
        layer_order.push(names);
    }

    // Build adjacency for the expanded graph (including dummies) for crossing minimization
    let mut adj_down: HashMap<String, Vec<String>> = HashMap::new(); // node -> children in next layer
    let mut adj_up: HashMap<String, Vec<String>> = HashMap::new();   // node -> parents in prev layer
    for ee in &expanded_edges {
        for (seg_from, seg_to) in &ee.segments {
            adj_down.entry(seg_from.clone()).or_default().push(seg_to.clone());
            adj_up.entry(seg_to.clone()).or_default().push(seg_from.clone());
        }
    }

    // --- Phase 3: Crossing minimization (barycenter heuristic) ---
    // Build position index for quick lookup
    let mut pos_in_layer: HashMap<String, usize> = HashMap::new();
    for lo in &layer_order {
        for (i, name) in lo.iter().enumerate() {
            pos_in_layer.insert(name.clone(), i);
        }
    }

    for _iteration in 0..crossing_iterations {
        // Top-down sweep
        for li in 1..layer_order.len() {
            let prev_layer = layer_order[li - 1].clone();
            let mut barycenters: Vec<(String, f64)> = Vec::new();
            for name in &layer_order[li] {
                if let Some(parents) = adj_up.get(name) {
                    let positions: Vec<f64> = parents
                        .iter()
                        .filter_map(|p| {
                            prev_layer.iter().position(|x| x == p).map(|pos| pos as f64)
                        })
                        .collect();
                    if positions.is_empty() {
                        barycenters.push((name.clone(), pos_in_layer.get(name).copied().unwrap_or(0) as f64));
                    } else {
                        let avg: f64 = positions.iter().sum::<f64>() / positions.len() as f64;
                        barycenters.push((name.clone(), avg));
                    }
                } else {
                    barycenters.push((name.clone(), pos_in_layer.get(name).copied().unwrap_or(0) as f64));
                }
            }
            barycenters.sort_by(|a, b| a.1.partial_cmp(&b.1).unwrap_or(std::cmp::Ordering::Equal));
            let new_order: Vec<String> = barycenters.into_iter().map(|(name, _)| name).collect();
            layer_order[li] = new_order;
            // Update position index for this layer
            for (i, name) in layer_order[li].iter().enumerate() {
                pos_in_layer.insert(name.clone(), i);
            }
        }

        // Bottom-up sweep
        for li in (0..layer_order.len().saturating_sub(1)).rev() {
            let next_layer = layer_order[li + 1].clone();
            let mut barycenters: Vec<(String, f64)> = Vec::new();
            for name in &layer_order[li] {
                if let Some(children) = adj_down.get(name) {
                    let positions: Vec<f64> = children
                        .iter()
                        .filter_map(|c| {
                            next_layer.iter().position(|x| x == c).map(|pos| pos as f64)
                        })
                        .collect();
                    if positions.is_empty() {
                        barycenters.push((name.clone(), pos_in_layer.get(name).copied().unwrap_or(0) as f64));
                    } else {
                        let avg: f64 = positions.iter().sum::<f64>() / positions.len() as f64;
                        barycenters.push((name.clone(), avg));
                    }
                } else {
                    barycenters.push((name.clone(), pos_in_layer.get(name).copied().unwrap_or(0) as f64));
                }
            }
            barycenters.sort_by(|a, b| a.1.partial_cmp(&b.1).unwrap_or(std::cmp::Ordering::Equal));
            let new_order: Vec<String> = barycenters.into_iter().map(|(name, _)| name).collect();
            layer_order[li] = new_order;
            for (i, name) in layer_order[li].iter().enumerate() {
                pos_in_layer.insert(name.clone(), i);
            }
        }
    }

    // --- Phase 4: Coordinate assignment (median positioning) ---
    // Assign x based on position in layer, y based on layer index
    let mut coords: HashMap<String, (f64, f64)> = HashMap::new();

    for (li, layer) in layer_order.iter().enumerate() {
        let layer_width = layer.len() as f64 * node_spacing;
        let x_offset = -layer_width / 2.0 + node_spacing / 2.0;
        let y = li as f64 * layer_spacing;

        for (pos, name) in layer.iter().enumerate() {
            let x = x_offset + pos as f64 * node_spacing;
            coords.insert(name.clone(), (x, y));
        }
    }

    // Center layers relative to each other using median of connected nodes
    // (second pass for refinement)
    for _pass in 0..2 {
        for li in 0..layer_order.len() {
            let layer = layer_order[li].clone();
            let mut new_xs: Vec<(String, f64)> = Vec::new();

            for name in &layer {
                let mut connected_xs: Vec<f64> = Vec::new();
                if let Some(parents) = adj_up.get(name) {
                    for p in parents {
                        if let Some(&(px, _)) = coords.get(p) {
                            connected_xs.push(px);
                        }
                    }
                }
                if let Some(children) = adj_down.get(name) {
                    for c in children {
                        if let Some(&(cx, _)) = coords.get(c) {
                            connected_xs.push(cx);
                        }
                    }
                }

                if connected_xs.is_empty() {
                    // Keep current position
                    if let Some(&(x, _)) = coords.get(name) {
                        new_xs.push((name.clone(), x));
                    }
                } else {
                    // Use median of connected x-coordinates
                    connected_xs.sort_by(|a, b| a.partial_cmp(b).unwrap_or(std::cmp::Ordering::Equal));
                    let median = if connected_xs.len() % 2 == 0 {
                        (connected_xs[connected_xs.len() / 2 - 1]
                            + connected_xs[connected_xs.len() / 2])
                            / 2.0
                    } else {
                        connected_xs[connected_xs.len() / 2]
                    };
                    new_xs.push((name.clone(), median));
                }
            }

            // Resolve overlaps: ensure minimum spacing
            new_xs.sort_by(|a, b| a.1.partial_cmp(&b.1).unwrap_or(std::cmp::Ordering::Equal));
            for i in 1..new_xs.len() {
                let prev_x = new_xs[i - 1].1;
                if new_xs[i].1 - prev_x < node_spacing {
                    new_xs[i].1 = prev_x + node_spacing;
                }
            }

            // Center the layer around 0
            if !new_xs.is_empty() {
                let min_x = new_xs.first().unwrap().1;
                let max_x = new_xs.last().unwrap().1;
                let center_offset = (min_x + max_x) / 2.0;
                for entry in &mut new_xs {
                    entry.1 -= center_offset;
                }
            }

            // Apply new x coordinates
            for (name, x) in &new_xs {
                if let Some(coord) = coords.get_mut(name) {
                    coord.0 = *x;
                }
            }
        }
    }

    // --- Build output ---
    // node_positions: only real nodes (no dummies)
    let mut node_positions: Vec<(String, f64, f64)> = Vec::new();
    let all_real_nodes: std::collections::HashSet<&String> = node_map.keys().collect();
    for name in &node_labels {
        if let Some(&(x, y)) = coords.get(name) {
            node_positions.push((name.clone(), x, y));
        }
    }
    // Also include nodes from edges not in labels
    for (a, b) in &edges {
        for n in [a, b] {
            if all_real_nodes.contains(n)
                && !node_positions.iter().any(|(name, _, _)| name == n)
            {
                if let Some(&(x, y)) = coords.get(n) {
                    node_positions.push((n.clone(), x, y));
                }
            }
        }
    }

    // edge_paths: polyline through dummy node positions
    let mut edge_paths: Vec<(String, String, Vec<(f64, f64)>)> = Vec::new();
    for ee in &expanded_edges {
        let mut waypoints: Vec<(f64, f64)> = Vec::new();

        // Start point
        if let Some(&(x, y)) = coords.get(&ee.from_label) {
            waypoints.push((x, y));
        }

        // Intermediate dummy points
        for (_seg_from, seg_to) in &ee.segments {
            // Add seg_to coords if it's a dummy node
            if seg_to.starts_with("__dummy_") {
                if let Some(&(x, y)) = coords.get(seg_to) {
                    waypoints.push((x, y));
                }
            }
        }

        // End point
        if let Some(&(x, y)) = coords.get(&ee.to_label) {
            waypoints.push((x, y));
        }

        edge_paths.push((ee.from_label.clone(), ee.to_label.clone(), waypoints));
    }

    // Build Python dict
    let dict = PyDict::new_bound(py);
    dict.set_item("node_positions", node_positions)?;
    dict.set_item("edge_paths", edge_paths)?;
    Ok(dict.into())
}


/// Assign layers using longest-path algorithm (source nodes at layer 0).
/// Each node's layer = max(layer of predecessors) + 1, or 0 if no predecessors.
fn assign_layers_longest_path(
    graph: &DiGraph<String, ()>,
    layer_of: &mut HashMap<NodeIndex, usize>,
) {
    use petgraph::visit::EdgeRef;

    let node_count = graph.node_count();
    if node_count == 0 {
        return;
    }

    // Build in-degree and adjacency
    let mut in_degree: HashMap<NodeIndex, usize> = HashMap::new();
    let mut successors: HashMap<NodeIndex, Vec<NodeIndex>> = HashMap::new();

    for nidx in graph.node_indices() {
        in_degree.entry(nidx).or_insert(0);
        successors.entry(nidx).or_insert_with(Vec::new);
    }

    for edge in graph.edge_references() {
        *in_degree.entry(edge.target()).or_insert(0) += 1;
        successors.entry(edge.source()).or_default().push(edge.target());
    }

    // Kahn's algorithm for topological order + longest path
    let mut queue: std::collections::VecDeque<NodeIndex> = std::collections::VecDeque::new();
    for (&node, &deg) in &in_degree {
        if deg == 0 {
            queue.push_back(node);
            layer_of.insert(node, 0);
        }
    }

    let mut remaining_in_degree = in_degree.clone();

    while let Some(node) = queue.pop_front() {
        let current_layer = *layer_of.get(&node).unwrap_or(&0);
        if let Some(succs) = successors.get(&node) {
            for &succ in succs {
                // Each successor's layer is at least one more than current
                let new_layer = current_layer + 1;
                let existing = layer_of.entry(succ).or_insert(0);
                if new_layer > *existing {
                    *existing = new_layer;
                }
                // Decrease in-degree
                if let Some(deg) = remaining_in_degree.get_mut(&succ) {
                    *deg -= 1;
                    if *deg == 0 {
                        queue.push_back(succ);
                    }
                }
            }
        }
    }

    // Handle nodes not reached (cycles) — assign to layer 0
    for nidx in graph.node_indices() {
        layer_of.entry(nidx).or_insert(0);
    }
}


/// Constrain nodes in the same phase group to share a layer.
/// Uses the maximum layer within each group so no node moves upward
/// past its topological position.
fn apply_phase_constraints(
    layer_of: &mut HashMap<NodeIndex, usize>,
    groups: &[(String, Vec<String>)],
    node_map: &HashMap<String, NodeIndex>,
) {
    for (_phase_name, members) in groups {
        // Find the maximum layer among group members
        let mut max_layer: usize = 0;
        let mut member_indices: Vec<NodeIndex> = Vec::new();
        for member in members {
            if let Some(&idx) = node_map.get(member) {
                member_indices.push(idx);
                if let Some(&layer) = layer_of.get(&idx) {
                    if layer > max_layer {
                        max_layer = layer;
                    }
                }
            }
        }
        // Set all members to the max layer
        for idx in member_indices {
            layer_of.insert(idx, max_layer);
        }
    }
}


pub fn register(parent: &Bound<'_, PyModule>) -> PyResult<()> {
    let m = PyModule::new_bound(parent.py(), "matrix")?;
    m.add_function(wrap_pyfunction!(harris_matrix_layout, &m)?)?;
    parent.add_submodule(&m)?;
    Ok(())
}
