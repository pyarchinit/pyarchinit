# -*- coding: utf-8 -*-
"""
R Analysis Functions for Archeozoology

Provides geostatistical and statistical analysis using R for zooarchaeological
quantification data. Includes semivariogram analysis, kriging, histograms,
boxplots, and other statistical visualizations.

@author: Enzo Cocca <enzo.ccc@gmail.com>
@date: 2024
"""

import os
from typing import Dict, List, Optional, Tuple, Any
from .r_session_manager import RSessionManager


class ArcheozooRAnalysis:
    """
    R-based analysis functions for archeozoology data.

    Provides methods for:
    - Database connection (PostgreSQL/SQLite)
    - Semivariogram calculation and visualization
    - Automated kriging with automap
    - Statistical plots (histograms, boxplots, coplots)
    - Correlation matrices
    - HTML report generation
    """

    def __init__(self):
        """Initialize the analysis class with R session manager."""
        self.r_manager = RSessionManager.get_instance()
        self._db_connected = False

    def is_r_available(self) -> bool:
        """Check if R is available for analysis."""
        return self.r_manager.is_available()

    def connect_to_database(
        self,
        db_type: str = 'postgres',
        host: str = 'localhost',
        port: int = 5432,
        database: str = '',
        user: str = '',
        password: str = ''
    ) -> bool:
        """
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
        """
        r = self.r_manager.get_session()

        try:
            if db_type == 'postgres':
                r('library(RPostgreSQL)')
                r('drv <- dbDriver("PostgreSQL")')
                r(f'con <- dbConnect(drv, host="{host}", dbname="{database}", '
                  f'port="{port}", password="{password}", user="{user}")')
            else:  # SQLite
                r('library(RSQLite)')
                r('drv <- dbDriver("SQLite")')
                r(f'con <- dbConnect(drv, dbname="{database}")')

            self._db_connected = True
            return True

        except Exception as e:
            print(f"Database connection error: {e}")
            self._db_connected = False
            return False

    def load_data(self, site_filter: Optional[str] = None) -> bool:
        """
        Load archeozoology data from the database into R.

        Args:
            site_filter: Optional site name to filter data.

        Returns:
            True if data loaded successfully, False otherwise.
        """
        if not self._db_connected:
            return False

        r = self.r_manager.get_session()

        try:
            if site_filter:
                r(f'archzoo_data <- dbGetQuery(con, "SELECT * FROM archeozoology_table WHERE sito = \'{site_filter}\'")')
            else:
                r('archzoo_data <- dbGetQuery(con, "SELECT * FROM archeozoology_table")')

            # Check if data was loaded
            r('data_rows <- nrow(archzoo_data)')
            rows = r.get('data_rows')

            return rows is not None and rows > 0

        except Exception as e:
            print(f"Data loading error: {e}")
            return False

    def calculate_semivariogram(
        self,
        variables: List[str],
        model: str = 'Sph',
        psill: float = 1.0,
        range_val: float = 100.0,
        nugget: float = 0.0,
        output_path: str = ''
    ) -> Optional[str]:
        """
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
        """
        r = self.r_manager.get_session()

        try:
            r('library(gstat)')
            r('library(sp)')

            # Create spatial points
            r('coordinates(archzoo_data) <- ~coord_x+coord_y')

            # Build gstat object with variables
            for i, var in enumerate(variables):
                if i == 0:
                    r(f'g <- gstat(NULL, "{var}", {var}~1, archzoo_data)')
                else:
                    r(f'g <- gstat(g, "{var}", {var}~1, archzoo_data)')

            # Calculate variogram
            r('v <- variogram(g)')

            # Fit model
            r(f'v_model <- vgm(psill={psill}, model="{model}", range={range_val}, nugget={nugget})')
            r('v_fit <- fit.variogram(v, v_model)')

            # Generate plot
            if output_path:
                plot_path = os.path.join(output_path, 'semivariogram.png')
                r(f'png("{plot_path}", width=3500, height=3500, res=400)')
                r('plot(v, v_fit, main="Semivariogram Analysis")')
                r('dev.off()')
                return plot_path

            return None

        except Exception as e:
            print(f"Semivariogram error: {e}")
            return None

    def run_automap_kriging(
        self,
        variable: str,
        model: str = 'Sph',
        output_path: str = '',
        fix_nugget: Optional[float] = None,
        fix_range: Optional[float] = None,
        fix_psill: Optional[float] = None
    ) -> Tuple[Optional[str], Optional[str]]:
        """
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
        """
        r = self.r_manager.get_session()

        try:
            r('library(automap)')
            r('library(raster)')
            r('library(sp)')

            # Ensure spatial coordinates
            r('if(!inherits(archzoo_data, "SpatialPointsDataFrame")) coordinates(archzoo_data) <- ~coord_x+coord_y')

            # Build fix.values
            nugget = 'NA' if fix_nugget is None else str(fix_nugget)
            range_v = 'NA' if fix_range is None else str(fix_range)
            psill = 'NA' if fix_psill is None else str(fix_psill)

            # Run autoKrige
            r(f'kriging_result <- autoKrige({variable}~1, archzoo_data, '
              f'model=c("{model}"), fix.values=c({nugget},{range_v},{psill}))')

            plot_path = None
            raster_path = None

            if output_path:
                # Generate kriging plot
                plot_path = os.path.join(output_path, f'kriging_{variable}.png')
                r(f'png("{plot_path}", width=3500, height=3500, res=400)')
                r('plot(kriging_result)')
                r('dev.off()')

                # Export as GeoTIFF
                raster_path = os.path.join(output_path, f'kriging_{variable}.tif')
                r(f'kriging_raster <- raster(kriging_result$krige_output)')
                r(f'writeRaster(kriging_raster, "{raster_path}", format="GTiff", overwrite=TRUE)')

            return plot_path, raster_path

        except Exception as e:
            print(f"Kriging error: {e}")
            return None, None

    def generate_histogram(
        self,
        variable: str,
        output_path: str = '',
        title: Optional[str] = None
    ) -> Optional[str]:
        """
        Generate histogram for a variable.

        Args:
            variable: Variable name to plot
            output_path: Path to save the plot
            title: Optional plot title

        Returns:
            Path to the generated plot, or None if failed.
        """
        r = self.r_manager.get_session()

        try:
            if title is None:
                title = f"Frequency Distribution - {variable}"

            if output_path:
                plot_path = os.path.join(output_path, f'{variable}_histogram.png')
                r(f'png("{plot_path}", width=2500, height=2500, res=400)')
                r(f'hist(archzoo_data${variable}, col="yellow", '
                  f'xlab="Quantity", ylab="Frequency", labels=TRUE, '
                  f'main="{title}")')
                r(f'abline(v=mean(archzoo_data${variable}, na.rm=TRUE), col="red", lwd=2)')
                r('dev.off()')
                return plot_path

            return None

        except Exception as e:
            print(f"Histogram error: {e}")
            return None

    def generate_boxplot(
        self,
        variable: str,
        output_path: str = ''
    ) -> Optional[str]:
        """
        Generate boxplot for a variable with statistical details.

        Args:
            variable: Variable name to plot
            output_path: Path to save the plot

        Returns:
            Path to the generated plot, or None if failed.
        """
        r = self.r_manager.get_session()

        try:
            if output_path:
                plot_path = os.path.join(output_path, f'{variable}_boxplot.png')
                r(f'png("{plot_path}", width=3500, height=3500, res=400)')
                r('op <- par(mar=c(0,5,0,0))')
                r('layout(matrix(c(1,1,1,2), nc=1))')
                r(f'a <- archzoo_data${variable}')
                r('boxplot(a, horizontal=TRUE, frame=FALSE, col="lightblue")')
                r('stripchart(a, method="jitter", pch=19, add=TRUE, col="blue")')
                r('par(op)')
                r('dev.off()')
                return plot_path

            return None

        except Exception as e:
            print(f"Boxplot error: {e}")
            return None

    def generate_coplot(
        self,
        variable: str,
        output_path: str = ''
    ) -> Optional[str]:
        """
        Generate conditional scatter plot (coplot) for spatial distribution.

        Args:
            variable: Variable name for conditioning
            output_path: Path to save the plot

        Returns:
            Path to the generated plot, or None if failed.
        """
        r = self.r_manager.get_session()

        try:
            r('library(lattice)')

            if output_path:
                plot_path = os.path.join(output_path, f'{variable}_coplot.png')
                r(f'png("{plot_path}", width=3500, height=3500, res=400)')
                r(f'coplot(coord_y ~ coord_x | {variable}, data=archzoo_data, '
                  f'overlap=0, cex=1, pch=20, col=1)')
                r('dev.off()')
                return plot_path

            return None

        except Exception as e:
            print(f"Coplot error: {e}")
            return None

    def generate_correlation_matrix(
        self,
        variables: List[str],
        output_path: str = ''
    ) -> Optional[str]:
        """
        Generate correlation matrix plot for multiple variables.

        Args:
            variables: List of variable names to correlate
            output_path: Path to save the plot

        Returns:
            Path to the generated plot, or None if failed.
        """
        r = self.r_manager.get_session()

        try:
            var_list = ', '.join([f'"{v}"' for v in variables])

            if output_path:
                plot_path = os.path.join(output_path, 'correlation_matrix.png')
                r(f'png("{plot_path}", width=3500, height=3500, res=400)')
                r(f'vars <- c({var_list})')
                r('subset_data <- archzoo_data[, vars]')
                r('cor_matrix <- cor(subset_data, use="complete.obs")')
                r('library(lattice)')
                r('levelplot(cor_matrix, main="Correlation Matrix", '
                  'xlab="", ylab="", scales=list(x=list(rot=45)))')
                r('dev.off()')
                return plot_path

            return None

        except Exception as e:
            print(f"Correlation matrix error: {e}")
            return None

    def generate_html_report(
        self,
        variables: List[str],
        output_path: str = '',
        title: str = 'Archeozoology Analysis Report'
    ) -> Optional[str]:
        """
        Generate HTML report with statistics and plots.

        Args:
            variables: List of variables to include in report
            output_path: Path to save the report
            title: Report title

        Returns:
            Path to the generated report, or None if failed.
        """
        r = self.r_manager.get_session()

        try:
            r('library(R2HTML)')

            if output_path:
                report_path = os.path.join(output_path, 'archeozoo_report.html')
                r(f'HTMLStart(outdir="{output_path}", filename="archeozoo_report", '
                  f'Title="{title}")')

                for var in variables:
                    r(f'HTML.title("{var} Analysis")')
                    r(f'HTML(summary(archzoo_data${var}))')

                r('HTMLStop()')
                return report_path

            return None

        except Exception as e:
            print(f"HTML report error: {e}")
            return None

    def close_connection(self) -> None:
        """Close the database connection in R."""
        if self._db_connected:
            try:
                r = self.r_manager.get_session()
                r('dbDisconnect(con)')
                self._db_connected = False
            except:
                pass

    def get_available_variables(self) -> List[str]:
        """
        Get list of numeric variables available in the loaded data.

        Returns:
            List of numeric column names.
        """
        r = self.r_manager.get_session()

        try:
            r('numeric_cols <- names(archzoo_data)[sapply(archzoo_data, is.numeric)]')
            return list(r.get('numeric_cols'))
        except:
            return []
