use pyo3::prelude::*;
use pyo3::types::{PyDict, PyList};
use rayon::prelude::*;

/// Fast geometry filter: given a list of WKB geometries with attributes,
/// filter by site name and return only matching records.
/// This is much faster than doing it in Python/SQLAlchemy.
#[pyfunction]
fn filter_geometries_by_site(
    gids: Vec<i64>,
    sitos: Vec<String>,
    target_site: String,
) -> PyResult<Vec<i64>> {
    // Parallel filter using rayon
    let result: Vec<i64> = gids
        .par_iter()
        .zip(sitos.par_iter())
        .filter(|(_, s)| **s == target_site)
        .map(|(g, _)| *g)
        .collect();
    Ok(result)
}

/// Build an IN() clause efficiently from a list of integers
#[pyfunction]
fn build_in_clause(ids: Vec<i64>) -> String {
    if ids.is_empty() {
        return "1=0".to_string(); // no match
    }
    let parts: Vec<String> = ids.iter().map(|id| id.to_string()).collect();
    format!("gid IN ({})", parts.join(","))
}

/// Fast categorization: given lists of d_stratigrafica values,
/// compute unique categories and assign colors deterministically.
/// Returns a dict of {category: (r, g, b)} color mapping.
#[pyfunction]
fn compute_style_categories(
    py: Python<'_>,
    d_stratigrafica_list: Vec<String>,
) -> PyResult<Py<PyDict>> {
    // Get unique values
    let mut unique: Vec<String> = d_stratigrafica_list
        .par_iter()
        .cloned()
        .collect::<std::collections::HashSet<String>>()
        .into_iter()
        .collect();
    unique.sort();

    // Generate deterministic colors using hash
    let dict = PyDict::new_bound(py);
    for (_i, cat) in unique.iter().enumerate() {
        let hash = cat.bytes().fold(0u64, |acc, b| acc.wrapping_mul(31).wrapping_add(b as u64));
        let r = ((hash >> 16) & 0xFF) as u8;
        let g = ((hash >> 8) & 0xFF) as u8;
        let b = (hash & 0xFF) as u8;
        let r = r.max(40);
        let g = g.max(40);
        let b = b.max(40);
        let color_tuple = (r, g, b);
        dict.set_item(cat, color_tuple)?;
    }
    Ok(dict.unbind())
}

/// Parse rapporti field (Python list-of-lists string) and extract relationships.
/// Much faster than ast.literal_eval in Python for large datasets.
#[pyfunction]
fn parse_rapporti_fast(rapporti_str: &str) -> PyResult<Vec<(String, String)>> {
    let mut results = Vec::new();

    if rapporti_str.is_empty() || rapporti_str == "[]" || rapporti_str == "[[]]" {
        return Ok(results);
    }

    // Simple parser for [[u'Type', u'Number'], ...] format
    let s = rapporti_str
        .replace("[", "")
        .replace("]", "")
        .replace("u'", "")
        .replace("'", "");

    let parts: Vec<&str> = s.split(',').collect();
    let mut i = 0;
    while i + 1 < parts.len() {
        let rel_type = parts[i].trim().to_string();
        let us_num = parts[i + 1].trim().to_string();
        if !rel_type.is_empty() && !us_num.is_empty() {
            results.push((rel_type, us_num));
        }
        i += 2;
    }

    Ok(results)
}

/// Batch parse rapporti for multiple US records in parallel.
/// Returns Vec of (us_number, Vec<(rel_type, related_us)>)
#[pyfunction]
fn batch_parse_rapporti(
    us_numbers: Vec<String>,
    rapporti_strings: Vec<String>,
) -> PyResult<Vec<(String, Vec<(String, String)>)>> {
    let results: Vec<(String, Vec<(String, String)>)> = us_numbers
        .par_iter()
        .zip(rapporti_strings.par_iter())
        .map(|(us, rapp)| {
            let parsed = parse_rapporti_fast_internal(rapp);
            (us.clone(), parsed)
        })
        .collect();
    Ok(results)
}

fn parse_rapporti_fast_internal(rapporti_str: &str) -> Vec<(String, String)> {
    let mut results = Vec::new();
    if rapporti_str.is_empty() || rapporti_str == "[]" || rapporti_str == "[[]]" {
        return results;
    }
    let s = rapporti_str
        .replace("[", "")
        .replace("]", "")
        .replace("u'", "")
        .replace("'", "");
    let parts: Vec<&str> = s.split(',').collect();
    let mut i = 0;
    while i + 1 < parts.len() {
        let rel_type = parts[i].trim().to_string();
        let us_num = parts[i + 1].trim().to_string();
        if !rel_type.is_empty() && !us_num.is_empty() {
            results.push((rel_type, us_num));
        }
        i += 2;
    }
    results
}

/// Build a relationship graph from US rapporti data.
/// Returns adjacency list as dict: {us_number: [(rel_type, related_us), ...]}
#[pyfunction]
fn build_relationship_graph(
    py: Python<'_>,
    us_numbers: Vec<String>,
    rapporti_strings: Vec<String>,
) -> PyResult<Py<PyDict>> {
    let graph = PyDict::new_bound(py);

    for (us, rapp) in us_numbers.iter().zip(rapporti_strings.iter()) {
        let relations = parse_rapporti_fast_internal(rapp);
        let py_list = PyList::empty_bound(py);
        for (rel_type, related) in relations {
            py_list.append((rel_type, related))?;
        }
        graph.set_item(us, py_list)?;
    }

    Ok(graph.unbind())
}

pub fn register(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(filter_geometries_by_site, m)?)?;
    m.add_function(wrap_pyfunction!(build_in_clause, m)?)?;
    m.add_function(wrap_pyfunction!(compute_style_categories, m)?)?;
    m.add_function(wrap_pyfunction!(parse_rapporti_fast, m)?)?;
    m.add_function(wrap_pyfunction!(batch_parse_rapporti, m)?)?;
    m.add_function(wrap_pyfunction!(build_relationship_graph, m)?)?;
    Ok(())
}
