use pyo3::prelude::*;

pub fn register(parent: &Bound<'_, PyModule>) -> PyResult<()> {
    let m = PyModule::new_bound(parent.py(), "matrix")?;
    // Layout functions will be added in Phase 4 (Harris Matrix layout)
    parent.add_submodule(&m)?;
    Ok(())
}
