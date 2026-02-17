use nalgebra::{DMatrix, DVector};
use pyo3::prelude::*;
use pyo3::exceptions::PyValueError;
use rayon::prelude::*;

// ---------------------------------------------------------------------------
// Variogram model evaluation
// ---------------------------------------------------------------------------

/// Evaluate a variogram model at distance h.
fn variogram_model(h: f64, nugget: f64, sill: f64, range_param: f64, model: &str) -> f64 {
    if h <= 0.0 {
        return 0.0; // gamma(0) = 0 by convention
    }
    match model {
        "spherical" => {
            if h >= range_param {
                sill
            } else {
                let hr = h / range_param;
                nugget + (sill - nugget) * (1.5 * hr - 0.5 * hr * hr * hr)
            }
        }
        "exponential" => nugget + (sill - nugget) * (1.0 - (-3.0 * h / range_param).exp()),
        "gaussian" => {
            let hr = h / range_param;
            nugget + (sill - nugget) * (1.0 - (-3.0 * hr * hr).exp())
        }
        "linear" => {
            let val = nugget + (sill - nugget) * (h / range_param);
            if val > sill {
                sill
            } else {
                val
            }
        }
        _ => sill, // unknown model -> pure sill
    }
}

/// Covariance = sill - gamma(h) for ordinary kriging.
#[inline]
fn covariance(h: f64, nugget: f64, sill: f64, range_param: f64, model: &str) -> f64 {
    sill - variogram_model(h, nugget, sill, range_param, model)
}

// ---------------------------------------------------------------------------
// Public functions exposed to Python
// ---------------------------------------------------------------------------

/// Calculate an empirical variogram from point data.
///
/// Returns `(lag_centers, semivariances)` as two vectors of equal length.
#[pyfunction]
#[pyo3(signature = (points_x, points_y, values, n_lags=20, max_lag=None))]
fn calculate_variogram(
    points_x: Vec<f64>,
    points_y: Vec<f64>,
    values: Vec<f64>,
    n_lags: usize,
    max_lag: Option<f64>,
) -> PyResult<(Vec<f64>, Vec<f64>)> {
    let n = points_x.len();
    if n != points_y.len() || n != values.len() {
        return Err(PyValueError::new_err(
            "points_x, points_y and values must have the same length",
        ));
    }
    if n < 2 {
        return Err(PyValueError::new_err("Need at least 2 points"));
    }
    if n_lags == 0 {
        return Err(PyValueError::new_err("n_lags must be > 0"));
    }

    // Compute max_lag if not provided (half of max pairwise distance)
    let max_lag = max_lag.unwrap_or_else(|| {
        let mut mx: f64 = 0.0;
        for i in 0..n {
            for j in (i + 1)..n {
                let dx = points_x[i] - points_x[j];
                let dy = points_y[i] - points_y[j];
                let d = (dx * dx + dy * dy).sqrt();
                if d > mx {
                    mx = d;
                }
            }
        }
        mx / 2.0
    });

    let lag_width = max_lag / n_lags as f64;

    // Precompute all pairwise (distance, squared_diff) in parallel
    // Pair index: for i < j, flat index = i * n - i*(i+1)/2 + (j - i - 1)
    let n_pairs_total = n * (n - 1) / 2;
    let pairs: Vec<(f64, f64)> = (0..n_pairs_total)
        .into_par_iter()
        .map(|flat| {
            // Decode flat index to (i, j)
            let i = decode_i(flat, n);
            let j = decode_j(flat, n, i);
            let dx = points_x[i] - points_x[j];
            let dy = points_y[i] - points_y[j];
            let dist = (dx * dx + dy * dy).sqrt();
            let sq_diff = (values[i] - values[j]).powi(2);
            (dist, sq_diff)
        })
        .collect();

    // Bin into lags
    let mut lag_centers: Vec<f64> = Vec::with_capacity(n_lags);
    let mut semivariances: Vec<f64> = Vec::with_capacity(n_lags);

    for lag_idx in 0..n_lags {
        let lag_min = lag_idx as f64 * lag_width;
        let lag_max = (lag_idx + 1) as f64 * lag_width;
        let mut sum_sq = 0.0;
        let mut count = 0u64;
        for &(d, sq) in &pairs {
            if d > lag_min && d <= lag_max {
                sum_sq += sq;
                count += 1;
            }
        }
        if count > 0 {
            lag_centers.push((lag_min + lag_max) / 2.0);
            semivariances.push(sum_sq / (2.0 * count as f64));
        }
    }

    Ok((lag_centers, semivariances))
}

/// Ordinary kriging interpolation on a regular grid.
///
/// Returns `(predictions_flat, variances_flat, ny, nx)` where
/// `predictions_flat` and `variances_flat` are row-major flat vectors.
#[pyfunction]
#[pyo3(signature = (
    points_x, points_y, values,
    grid_x, grid_y,
    variogram_model_name = "spherical",
    nugget = 0.0,
    sill = 1.0,
    range_param = 100.0,
    max_nearby = 20
))]
fn ordinary_kriging(
    points_x: Vec<f64>,
    points_y: Vec<f64>,
    values: Vec<f64>,
    grid_x: Vec<f64>,
    grid_y: Vec<f64>,
    variogram_model_name: &str,
    nugget: f64,
    sill: f64,
    range_param: f64,
    max_nearby: usize,
) -> PyResult<(Vec<f64>, Vec<f64>, usize, usize)> {
    let n_pts = points_x.len();
    if n_pts != points_y.len() || n_pts != values.len() {
        return Err(PyValueError::new_err(
            "points_x, points_y and values must have the same length",
        ));
    }
    if n_pts < 3 {
        return Err(PyValueError::new_err("Need at least 3 points"));
    }

    let nx = grid_x.len();
    let ny = grid_y.len();
    let n_cells = ny * nx;

    let model = variogram_model_name.to_string();
    let mean_val: f64 = values.iter().sum::<f64>() / n_pts as f64;

    // For each grid cell, perform ordinary kriging
    let results: Vec<(f64, f64)> = (0..n_cells)
        .into_par_iter()
        .map(|cell_idx| {
            let iy = cell_idx / nx;
            let ix = cell_idx % nx;
            let gx = grid_x[ix];
            let gy = grid_y[iy];

            // Compute distances to all data points
            let mut dist_idx: Vec<(f64, usize)> = (0..n_pts)
                .map(|k| {
                    let dx = points_x[k] - gx;
                    let dy = points_y[k] - gy;
                    ((dx * dx + dy * dy).sqrt(), k)
                })
                .collect();

            // Filter to within 3 * range
            let search_dist = range_param * 3.0;
            dist_idx.retain(|&(d, _)| d < search_dist);

            if dist_idx.len() < 3 {
                return (mean_val, sill);
            }

            // Sort by distance, take closest max_nearby
            dist_idx.sort_by(|a, b| a.0.partial_cmp(&b.0).unwrap());
            if dist_idx.len() > max_nearby {
                dist_idx.truncate(max_nearby);
            }

            let nn = dist_idx.len();

            // Build kriging system: (nn+1) x (nn+1)
            let size = nn + 1;
            let mut k_mat = DMatrix::<f64>::zeros(size, size);
            let mut k_vec = DVector::<f64>::zeros(size);

            // Fill covariance matrix
            for a in 0..nn {
                k_mat[(a, a)] = sill; // C(0) = sill
                for b in (a + 1)..nn {
                    let dx = points_x[dist_idx[a].1] - points_x[dist_idx[b].1];
                    let dy = points_y[dist_idx[a].1] - points_y[dist_idx[b].1];
                    let h = (dx * dx + dy * dy).sqrt();
                    let c = covariance(h, nugget, sill, range_param, &model);
                    k_mat[(a, b)] = c;
                    k_mat[(b, a)] = c;
                }
            }

            // Lagrange multiplier row/col
            for a in 0..nn {
                k_mat[(nn, a)] = 1.0;
                k_mat[(a, nn)] = 1.0;
            }
            k_mat[(nn, nn)] = 0.0;

            // Fill covariance vector (target to data)
            for a in 0..nn {
                let c = covariance(dist_idx[a].0, nugget, sill, range_param, &model);
                k_vec[a] = c;
            }
            k_vec[nn] = 1.0;

            // Add small regularization for numerical stability
            for a in 0..nn {
                k_mat[(a, a)] += 1e-8 * sill;
            }

            // Solve
            match k_mat.clone().lu().solve(&k_vec) {
                Some(weights) => {
                    let mut pred = 0.0;
                    for a in 0..nn {
                        pred += weights[a] * values[dist_idx[a].1];
                    }
                    let mut var = sill;
                    for a in 0..nn {
                        var -= weights[a] * k_vec[a];
                    }
                    var -= weights[nn];
                    if !pred.is_finite() || !var.is_finite() {
                        (mean_val, sill)
                    } else {
                        (pred, var.max(0.0))
                    }
                }
                None => (mean_val, sill),
            }
        })
        .collect();

    let predictions: Vec<f64> = results.iter().map(|r| r.0).collect();
    let variances: Vec<f64> = results.iter().map(|r| r.1).collect();

    Ok((predictions, variances, ny, nx))
}

/// Inverse Distance Weighting interpolation on a regular grid.
///
/// Returns `(predictions_flat, ny, nx)`.
#[pyfunction]
#[pyo3(signature = (
    points_x, points_y, values,
    grid_x, grid_y,
    power = 2.0,
    search_radius = None
))]
fn idw_interpolation(
    points_x: Vec<f64>,
    points_y: Vec<f64>,
    values: Vec<f64>,
    grid_x: Vec<f64>,
    grid_y: Vec<f64>,
    power: f64,
    search_radius: Option<f64>,
) -> PyResult<(Vec<f64>, usize, usize)> {
    let n_pts = points_x.len();
    if n_pts != points_y.len() || n_pts != values.len() {
        return Err(PyValueError::new_err(
            "points_x, points_y and values must have the same length",
        ));
    }
    if n_pts == 0 {
        return Err(PyValueError::new_err("Need at least 1 point"));
    }

    let nx = grid_x.len();
    let ny = grid_y.len();
    let n_cells = ny * nx;

    let predictions: Vec<f64> = (0..n_cells)
        .into_par_iter()
        .map(|cell_idx| {
            let iy = cell_idx / nx;
            let ix = cell_idx % nx;
            let gx = grid_x[ix];
            let gy = grid_y[iy];

            let mut w_sum = 0.0;
            let mut wv_sum = 0.0;
            let mut exact_val: Option<f64> = None;

            for k in 0..n_pts {
                let dx = points_x[k] - gx;
                let dy = points_y[k] - gy;
                let d = (dx * dx + dy * dy).sqrt();

                // Apply search radius filter
                if let Some(sr) = search_radius {
                    if d > sr {
                        continue;
                    }
                }

                if d == 0.0 {
                    exact_val = Some(values[k]);
                    break;
                }

                let w = 1.0 / d.powf(power);
                w_sum += w;
                wv_sum += w * values[k];
            }

            if let Some(v) = exact_val {
                v
            } else if w_sum > 0.0 {
                wv_sum / w_sum
            } else {
                f64::NAN
            }
        })
        .collect();

    Ok((predictions, ny, nx))
}

/// Maximin sampling design.
///
/// From `n_candidates` random points within the bounding box of existing
/// points (with 20% buffer), greedily select `n_new` points that maximize
/// the minimum distance to all existing + already-selected points.
///
/// Returns `(new_x, new_y)`.
#[pyfunction]
#[pyo3(signature = (existing_x, existing_y, n_new, n_candidates = 1000))]
fn maximin_design(
    existing_x: Vec<f64>,
    existing_y: Vec<f64>,
    n_new: usize,
    n_candidates: usize,
) -> PyResult<(Vec<f64>, Vec<f64>)> {
    let n_existing = existing_x.len();
    if n_existing != existing_y.len() {
        return Err(PyValueError::new_err(
            "existing_x and existing_y must have the same length",
        ));
    }
    if n_existing == 0 {
        return Err(PyValueError::new_err("Need at least 1 existing point"));
    }
    if n_new == 0 {
        return Ok((vec![], vec![]));
    }

    // Compute bounding box with 20% buffer
    let xmin = existing_x.iter().cloned().fold(f64::INFINITY, f64::min);
    let xmax = existing_x.iter().cloned().fold(f64::NEG_INFINITY, f64::max);
    let ymin = existing_y.iter().cloned().fold(f64::INFINITY, f64::min);
    let ymax = existing_y.iter().cloned().fold(f64::NEG_INFINITY, f64::max);
    let x_buf = (xmax - xmin) * 0.2;
    let y_buf = (ymax - ymin) * 0.2;
    let xmin = xmin - x_buf;
    let xmax = xmax + x_buf;
    let ymin = ymin - y_buf;
    let ymax = ymax + y_buf;

    // Generate candidate points using a simple LCG PRNG (deterministic)
    let mut rng_state: u64 = 42;
    let mut next_rand = || -> f64 {
        // Linear congruential generator
        rng_state = rng_state.wrapping_mul(6364136223846793005).wrapping_add(1442695040888963407);
        // Map to [0, 1)
        (rng_state >> 33) as f64 / (1u64 << 31) as f64
    };

    let mut cand_x: Vec<f64> = Vec::with_capacity(n_candidates);
    let mut cand_y: Vec<f64> = Vec::with_capacity(n_candidates);
    for _ in 0..n_candidates {
        cand_x.push(xmin + next_rand() * (xmax - xmin));
        cand_y.push(ymin + next_rand() * (ymax - ymin));
    }

    // Greedy maximin selection
    let mut all_x: Vec<f64> = existing_x.clone();
    let mut all_y: Vec<f64> = existing_y.clone();
    let mut selected_x: Vec<f64> = Vec::with_capacity(n_new);
    let mut selected_y: Vec<f64> = Vec::with_capacity(n_new);
    let mut used: Vec<bool> = vec![false; n_candidates];

    for _ in 0..n_new {
        let mut best_idx: usize = 0;
        let mut best_min_dist: f64 = f64::NEG_INFINITY;

        for c in 0..n_candidates {
            if used[c] {
                continue;
            }
            let cx = cand_x[c];
            let cy = cand_y[c];

            // Minimum distance to all existing + selected points
            let mut min_d = f64::INFINITY;
            for k in 0..all_x.len() {
                let dx = all_x[k] - cx;
                let dy = all_y[k] - cy;
                let d = (dx * dx + dy * dy).sqrt();
                if d < min_d {
                    min_d = d;
                }
            }

            if min_d > best_min_dist {
                best_min_dist = min_d;
                best_idx = c;
            }
        }

        used[best_idx] = true;
        let sx = cand_x[best_idx];
        let sy = cand_y[best_idx];
        selected_x.push(sx);
        selected_y.push(sy);
        all_x.push(sx);
        all_y.push(sy);
    }

    Ok((selected_x, selected_y))
}

/// Leave-one-out cross-validation for ordinary kriging.
///
/// Returns `(rmse, mae)`.
#[pyfunction]
#[pyo3(signature = (
    points_x, points_y, values,
    variogram_model_name = "spherical",
    nugget = 0.0,
    sill = 1.0,
    range_param = 100.0,
    max_cv_points = 50,
    max_nearby = 30
))]
fn cross_validate_kriging(
    points_x: Vec<f64>,
    points_y: Vec<f64>,
    values: Vec<f64>,
    variogram_model_name: &str,
    nugget: f64,
    sill: f64,
    range_param: f64,
    max_cv_points: usize,
    max_nearby: usize,
) -> PyResult<(f64, f64)> {
    let n = points_x.len();
    if n != points_y.len() || n != values.len() {
        return Err(PyValueError::new_err(
            "points_x, points_y and values must have the same length",
        ));
    }
    if n < 4 {
        return Err(PyValueError::new_err("Need at least 4 points"));
    }

    // Determine indices to cross-validate
    let cv_indices: Vec<usize> = if n > max_cv_points {
        // Deterministic subsampling: evenly spaced
        let step = n as f64 / max_cv_points as f64;
        (0..max_cv_points).map(|k| (k as f64 * step) as usize).collect()
    } else {
        (0..n).collect()
    };

    let model = variogram_model_name.to_string();

    // Parallel leave-one-out
    let errors: Vec<Option<f64>> = cv_indices
        .par_iter()
        .map(|&i| {
            // Build training set (all points except i)
            let mut train_dist: Vec<(f64, usize)> = Vec::with_capacity(n - 1);
            for k in 0..n {
                if k == i {
                    continue;
                }
                let dx = points_x[k] - points_x[i];
                let dy = points_y[k] - points_y[i];
                let d = (dx * dx + dy * dy).sqrt();
                if d < range_param * 3.0 {
                    train_dist.push((d, k));
                }
            }

            if train_dist.len() < 3 {
                return None;
            }

            // Sort and take closest
            train_dist.sort_by(|a, b| a.0.partial_cmp(&b.0).unwrap());
            if train_dist.len() > max_nearby {
                train_dist.truncate(max_nearby);
            }

            let nn = train_dist.len();
            let size = nn + 1;

            // Build kriging system
            let mut k_mat = DMatrix::<f64>::zeros(size, size);
            let mut k_vec = DVector::<f64>::zeros(size);

            for a in 0..nn {
                k_mat[(a, a)] = sill;
                for b in (a + 1)..nn {
                    let dx = points_x[train_dist[a].1] - points_x[train_dist[b].1];
                    let dy = points_y[train_dist[a].1] - points_y[train_dist[b].1];
                    let h = (dx * dx + dy * dy).sqrt();
                    let c = covariance(h, nugget, sill, range_param, &model);
                    k_mat[(a, b)] = c;
                    k_mat[(b, a)] = c;
                }
            }
            for a in 0..nn {
                k_mat[(nn, a)] = 1.0;
                k_mat[(a, nn)] = 1.0;
            }
            k_mat[(nn, nn)] = 0.0;

            for a in 0..nn {
                let c = covariance(train_dist[a].0, nugget, sill, range_param, &model);
                k_vec[a] = c;
            }
            k_vec[nn] = 1.0;

            // Regularization
            for a in 0..nn {
                k_mat[(a, a)] += 1e-10;
            }

            match k_mat.lu().solve(&k_vec) {
                Some(weights) => {
                    let mut pred = 0.0;
                    for a in 0..nn {
                        pred += weights[a] * values[train_dist[a].1];
                    }
                    if pred.is_finite() {
                        Some(pred - values[i])
                    } else {
                        None
                    }
                }
                None => None,
            }
        })
        .collect();

    // Compute RMSE and MAE from valid errors
    let valid_errors: Vec<f64> = errors.iter().filter_map(|e| *e).collect();
    if valid_errors.is_empty() {
        return Ok((0.0, 0.0));
    }

    let mse: f64 = valid_errors.iter().map(|e| e * e).sum::<f64>() / valid_errors.len() as f64;
    let rmse = mse.sqrt();
    let mae: f64 =
        valid_errors.iter().map(|e| e.abs()).sum::<f64>() / valid_errors.len() as f64;

    Ok((rmse, mae))
}

// ---------------------------------------------------------------------------
// Utility: decode flat pair index to (i, j) where i < j
// ---------------------------------------------------------------------------

#[inline]
fn decode_i(flat: usize, n: usize) -> usize {
    // For pair index flat with i < j:
    // flat = i * n - i*(i+1)/2 + (j - i - 1)
    // We can find i by scanning or with a formula
    let mut i = 0usize;
    let mut remaining = flat;
    loop {
        let row_size = n - i - 1;
        if remaining < row_size {
            return i;
        }
        remaining -= row_size;
        i += 1;
    }
}

#[inline]
fn decode_j(flat: usize, n: usize, i: usize) -> usize {
    let row_start = i * n - i * (i + 1) / 2;
    i + 1 + (flat - row_start)
}

// ---------------------------------------------------------------------------
// Module registration
// ---------------------------------------------------------------------------

pub fn register(parent: &Bound<'_, PyModule>) -> PyResult<()> {
    let m = PyModule::new_bound(parent.py(), "geostat")?;
    m.add_function(wrap_pyfunction!(calculate_variogram, &m)?)?;
    m.add_function(wrap_pyfunction!(ordinary_kriging, &m)?)?;
    m.add_function(wrap_pyfunction!(idw_interpolation, &m)?)?;
    m.add_function(wrap_pyfunction!(maximin_design, &m)?)?;
    m.add_function(wrap_pyfunction!(cross_validate_kriging, &m)?)?;
    parent.add_submodule(&m)?;
    Ok(())
}
