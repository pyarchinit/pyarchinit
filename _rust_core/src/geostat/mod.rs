use pyo3::prelude::*;

pub fn register(parent: &Bound<'_, PyModule>) -> PyResult<()> {
    let m = PyModule::new_bound(parent.py(), "geostat")?;
    // Functions will be added in Phase 3 (kriging, variogram, IDW, maximin)
    parent.add_submodule(&m)?;
    Ok(())
}
