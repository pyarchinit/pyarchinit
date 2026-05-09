# modules/r_integration/archeozoo_r_analysis.py

## Overview

This file contains 15 documented elements.

## Classes

### ArcheozooRAnalysis

R-based analysis functions for archeozoology data.

Provides methods for:
- Database connection (PostgreSQL/SQLite)
- Semivariogram calculation and visualization
- Automated kriging with automap
- Statistical plots (histograms, boxplots, coplots)
- Correlation matrices
- HTML report generation

#### Methods

##### __init__(self)

Initialize the analysis class with R session manager.

##### is_r_available(self)

Check if R is available for analysis.

##### connect_to_database(self, db_type, host, port, database, user, password)

Establish R connection to the database.

Args:
    db_type: Database type ('postgres' or 'sqlite')
    host: Database host (for PostgreSQL)
    port: Database port (for PostgreSQL)
    database: Database name or path
    user: Database user (for PostgreSQL)
    password: Database password (for PostgreSQL)

Returns:
    True if connection successful, False otherwise.

##### load_data(self, site_filter)

Load archeozoology data from the database into R.

Args:
    site_filter: Optional site name to filter data.

Returns:
    True if data loaded successfully, False otherwise.

##### calculate_semivariogram(self, variables, model, psill, range_val, nugget, output_path)

Calculate and plot semivariogram for selected variables.

Args:
    variables: List of variable names to analyze
    model: Variogram model type ('Sph', 'Exp', 'Gau', 'Mat')
    psill: Sill parameter
    range_val: Range parameter
    nugget: Nugget parameter
    output_path: Path to save the output plot

Returns:
    Path to the generated plot, or None if failed.

##### run_automap_kriging(self, variable, model, output_path, fix_nugget, fix_range, fix_psill)

Run automated kriging using the automap package.

Args:
    variable: Variable name to krige
    model: Variogram model type
    output_path: Path to save outputs
    fix_nugget: Fixed nugget value (optional)
    fix_range: Fixed range value (optional)
    fix_psill: Fixed psill value (optional)

Returns:
    Tuple of (plot_path, raster_path) or (None, None) if failed.

##### generate_histogram(self, variable, output_path, title)

Generate histogram for a variable.

Args:
    variable: Variable name to plot
    output_path: Path to save the plot
    title: Optional plot title

Returns:
    Path to the generated plot, or None if failed.

##### generate_boxplot(self, variable, output_path)

Generate boxplot for a variable with statistical details.

Args:
    variable: Variable name to plot
    output_path: Path to save the plot

Returns:
    Path to the generated plot, or None if failed.

##### generate_coplot(self, variable, output_path)

Generate conditional scatter plot (coplot) for spatial distribution.

Args:
    variable: Variable name for conditioning
    output_path: Path to save the plot

Returns:
    Path to the generated plot, or None if failed.

##### generate_correlation_matrix(self, variables, output_path)

Generate correlation matrix plot for multiple variables.

Args:
    variables: List of variable names to correlate
    output_path: Path to save the plot

Returns:
    Path to the generated plot, or None if failed.

##### generate_html_report(self, variables, output_path, title)

Generate HTML report with statistics and plots.

Args:
    variables: List of variables to include in report
    output_path: Path to save the report
    title: Report title

Returns:
    Path to the generated report, or None if failed.

##### close_connection(self)

Close the database connection in R.

##### get_available_variables(self)

Get list of numeric variables available in the loaded data.

Returns:
    List of numeric column names.

