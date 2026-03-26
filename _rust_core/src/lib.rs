use pyo3::prelude::*;

mod geostat;
mod graph;
mod matrix;
mod spatial;

/// PyArchInit Rust acceleration module
#[pymodule]
fn pyarchinit_core(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add("__version__", env!("CARGO_PKG_VERSION"))?;
    geostat::register(m)?;
    graph::register(m)?;
    matrix::register(m)?;
    spatial::register(m)?;
    Ok(())
}
