use pyo3::prelude::*;
use std::collections::{HashMap, HashSet, VecDeque};

/// Topological sort with level grouping (Kahn's algorithm)
#[pyfunction]
#[pyo3(signature = (edges, reverse_order=true))]
fn topological_sort_with_levels(
    edges: Vec<(String, String)>,
    reverse_order: bool,
) -> PyResult<Vec<Vec<String>>> {
    // Collect all nodes
    let mut all_nodes: HashSet<String> = HashSet::new();
    let mut adjacency: HashMap<String, HashSet<String>> = HashMap::new();
    let mut in_degree: HashMap<String, usize> = HashMap::new();

    for (from, to) in &edges {
        all_nodes.insert(from.clone());
        all_nodes.insert(to.clone());
        adjacency.entry(from.clone()).or_default().insert(to.clone());
        *in_degree.entry(to.clone()).or_insert(0) += 1;
        in_degree.entry(from.clone()).or_insert(0);
    }

    // Kahn's algorithm with level tracking
    let mut queue: VecDeque<String> = all_nodes
        .iter()
        .filter(|n| *in_degree.get(*n).unwrap_or(&0) == 0)
        .cloned()
        .collect();

    let mut levels: Vec<Vec<String>> = Vec::new();
    let mut processed: HashSet<String> = HashSet::new();

    while !queue.is_empty() {
        let mut current_level: Vec<String> = Vec::new();
        let mut next_queue: VecDeque<String> = VecDeque::new();

        for node in queue.drain(..) {
            if processed.contains(&node) {
                continue;
            }
            current_level.push(node.clone());
            processed.insert(node.clone());

            if let Some(neighbors) = adjacency.get(&node) {
                for neighbor in neighbors {
                    if let Some(deg) = in_degree.get_mut(neighbor) {
                        *deg -= 1;
                        if *deg == 0 {
                            next_queue.push_back(neighbor.clone());
                        }
                    }
                }
            }
        }

        if !current_level.is_empty() {
            current_level.sort();
            levels.push(current_level);
        }
        queue = next_queue;
    }

    // Add unprocessed nodes (cycles) as final level
    let unprocessed: Vec<String> = all_nodes.difference(&processed).cloned().collect();
    if !unprocessed.is_empty() {
        let mut sorted = unprocessed;
        sorted.sort();
        levels.push(sorted);
    }

    if reverse_order {
        levels.reverse();
    }

    Ok(levels)
}

/// Detect and remove cycles from a directed graph
#[pyfunction]
fn detect_and_remove_cycles(
    edges: Vec<(String, String)>,
) -> PyResult<(Vec<(String, String)>, Vec<Vec<String>>)> {
    let mut adjacency: HashMap<String, HashSet<String>> = HashMap::new();
    let mut all_nodes: HashSet<String> = HashSet::new();

    for (from, to) in &edges {
        all_nodes.insert(from.clone());
        all_nodes.insert(to.clone());
        adjacency.entry(from.clone()).or_default().insert(to.clone());
    }

    // Iterative DFS for cycle detection
    let mut color: HashMap<String, u8> = all_nodes.iter().map(|n| (n.clone(), 0u8)).collect();
    let mut cycles: Vec<Vec<String>> = Vec::new();
    let mut edges_to_remove: Vec<(String, String)> = Vec::new();

    for start in &all_nodes {
        if color[start] != 0 {
            continue;
        }

        let mut path: Vec<String> = vec![start.clone()];
        let mut path_set: HashSet<String> = HashSet::from([start.clone()]);
        *color.get_mut(start).unwrap() = 1; // GRAY

        let mut neighbor_iters: Vec<Box<dyn Iterator<Item = String>>> = vec![Box::new(
            adjacency
                .get(start)
                .cloned()
                .unwrap_or_default()
                .into_iter(),
        )];

        while let Some(iter) = neighbor_iters.last_mut() {
            if let Some(neighbor) = iter.next() {
                if color.get(&neighbor) == Some(&1) && path_set.contains(&neighbor) {
                    if let Some(pos) = path.iter().position(|n| n == &neighbor) {
                        let cycle: Vec<String> = path[pos..].to_vec();
                        if cycle.len() >= 2 {
                            let from = cycle.last().unwrap().clone();
                            let to = cycle[0].clone();
                            edges_to_remove.push((from, to));
                        }
                        cycles.push(cycle);
                    }
                } else if color.get(&neighbor) == Some(&0) {
                    *color.get_mut(&neighbor).unwrap() = 1;
                    path.push(neighbor.clone());
                    path_set.insert(neighbor.clone());
                    neighbor_iters.push(Box::new(
                        adjacency
                            .get(&neighbor)
                            .cloned()
                            .unwrap_or_default()
                            .into_iter(),
                    ));
                }
            } else {
                if let Some(node) = path.pop() {
                    path_set.remove(&node);
                    *color.get_mut(&node).unwrap() = 2; // BLACK
                }
                neighbor_iters.pop();
            }
        }
    }

    // Remove cycle edges from adjacency
    for (from, to) in &edges_to_remove {
        if let Some(neighbors) = adjacency.get_mut(from) {
            neighbors.remove(to);
        }
    }

    // Rebuild clean edge list
    let clean_edges: Vec<(String, String)> = adjacency
        .iter()
        .flat_map(|(from, tos)| tos.iter().map(move |to| (from.clone(), to.clone())))
        .collect();

    Ok((clean_edges, cycles))
}

/// Transitive reduction of a DAG (replaces `tred` subprocess)
#[pyfunction]
fn transitive_reduction(edges: Vec<(String, String)>) -> PyResult<Vec<(String, String)>> {
    // Build node index
    let mut node_to_idx: HashMap<String, usize> = HashMap::new();
    let mut idx_to_node: Vec<String> = Vec::new();

    for (from, to) in &edges {
        for node in [from, to] {
            if !node_to_idx.contains_key(node) {
                let idx = idx_to_node.len();
                node_to_idx.insert(node.clone(), idx);
                idx_to_node.push(node.clone());
            }
        }
    }

    let n = idx_to_node.len();
    if n == 0 {
        return Ok(vec![]);
    }

    // Build adjacency matrix
    let mut adj: Vec<Vec<bool>> = vec![vec![false; n]; n];
    for (from, to) in &edges {
        let i = node_to_idx[from];
        let j = node_to_idx[to];
        adj[i][j] = true;
    }

    // Compute transitive closure (Warshall's algorithm)
    let mut reach = adj.clone();
    for k in 0..n {
        for i in 0..n {
            for j in 0..n {
                if reach[i][k] && reach[k][j] {
                    reach[i][j] = true;
                }
            }
        }
    }

    // Remove transitive edges
    let mut reduced: Vec<(String, String)> = Vec::new();
    for (from, to) in &edges {
        let i = node_to_idx[from];
        let j = node_to_idx[to];

        // Keep edge i->j only if there's no intermediate path
        let mut is_transitive = false;
        for k in 0..n {
            if k != i && k != j && adj[i][k] && reach[k][j] {
                is_transitive = true;
                break;
            }
        }

        if !is_transitive {
            reduced.push((from.clone(), to.clone()));
        }
    }

    Ok(reduced)
}

pub fn register(parent: &Bound<'_, PyModule>) -> PyResult<()> {
    let m = PyModule::new_bound(parent.py(), "graph")?;
    m.add_function(wrap_pyfunction!(topological_sort_with_levels, &m)?)?;
    m.add_function(wrap_pyfunction!(detect_and_remove_cycles, &m)?)?;
    m.add_function(wrap_pyfunction!(transitive_reduction, &m)?)?;
    parent.add_submodule(&m)?;
    Ok(())
}
