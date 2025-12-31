# -*- coding: utf-8 -*-
"""
R Session Manager for PyArchInit Archeozoology Module

Manages R sessions and provides geostatistical analysis functions using PyPER.
This module provides a singleton pattern for R session management and handles
all R-related operations for the Archeozoology statistical analysis.

@author: Enzo Cocca <enzo.ccc@gmail.com>
@date: 2024
"""

import os
import sys
from typing import Dict, List, Optional, Any


class RSessionManager:
    """
    Singleton class for managing R session lifecycle.

    Provides methods to:
    - Check R availability
    - Initialize and manage R sessions
    - Check and install required R packages
    - Execute R code safely
    """

    _instance = None
    _r_session = None
    _r_available = None
    _r_checked = False

    # Required R packages for Archeozoology analysis
    REQUIRED_PACKAGES = [
        'RPostgreSQL',  # PostgreSQL database connection
        'RSQLite',      # SQLite database connection
        'gstat',        # Geostatistical modeling and kriging
        'automap',      # Automated variogram fitting and kriging
        'raster',       # Raster data handling and GeoTIFF export
        'lattice',      # Advanced statistical graphics
        'R2HTML',       # HTML report generation
        'sp'            # Spatial data classes and methods
    ]

    def __new__(cls):
        """Singleton pattern implementation."""
        if cls._instance is None:
            cls._instance = super(RSessionManager, cls).__new__(cls)
        return cls._instance

    @classmethod
    def get_instance(cls) -> 'RSessionManager':
        """Get the singleton instance of RSessionManager."""
        if cls._instance is None:
            cls._instance = RSessionManager()
        return cls._instance

    def __init__(self):
        """Initialize the R session manager."""
        if not self._r_checked:
            self._check_r_availability()
            RSessionManager._r_checked = True

    def _check_r_availability(self) -> None:
        """
        Check if R is installed and PyPER is available.

        Sets _r_available to True if R can be initialized, False otherwise.
        """
        try:
            from pyper import R
            # Try to create an R session
            self._r_session = R(use_numpy=True)
            # Test that R is working
            self._r_session('x <- 1')
            RSessionManager._r_available = True
        except ImportError:
            RSessionManager._r_available = False
            RSessionManager._r_session = None
        except Exception as e:
            RSessionManager._r_available = False
            RSessionManager._r_session = None
            print(f"R initialization error: {e}")

    def is_available(self) -> bool:
        """
        Check if R is available for use.

        Returns:
            True if R is installed and PyPER can connect to it, False otherwise.
        """
        return self._r_available

    def get_session(self) -> Any:
        """
        Get the R session, creating one if necessary.

        Returns:
            The R session object from PyPER.

        Raises:
            RuntimeError: If R is not available.
        """
        if not self._r_available:
            raise RuntimeError(
                "R is not available. Please install R and PyPER.\n"
                "1. Install R from https://cran.r-project.org/\n"
                "2. Install PyPER: pip install pyper"
            )

        if self._r_session is None:
            from pyper import R
            RSessionManager._r_session = R(use_numpy=True)

        return self._r_session

    def check_packages(self) -> Dict[str, bool]:
        """
        Check which required R packages are installed.

        Returns:
            Dictionary mapping package names to their installation status.
        """
        if not self._r_available:
            return {pkg: False for pkg in self.REQUIRED_PACKAGES}

        results = {}
        r = self.get_session()

        for pkg in self.REQUIRED_PACKAGES:
            try:
                r(f'pkg_available <- suppressWarnings(require("{pkg}", quietly=TRUE))')
                results[pkg] = r.get('pkg_available')
            except:
                results[pkg] = False

        return results

    def get_missing_packages(self) -> List[str]:
        """
        Get list of required packages that are not installed.

        Returns:
            List of package names that need to be installed.
        """
        package_status = self.check_packages()
        return [pkg for pkg, installed in package_status.items() if not installed]

    def install_packages(self, packages: Optional[List[str]] = None) -> bool:
        """
        Install R packages from CRAN.

        Args:
            packages: List of package names to install.
                      If None, installs all missing required packages.

        Returns:
            True if installation was attempted, False if R is not available.
        """
        if not self._r_available:
            return False

        if packages is None:
            packages = self.get_missing_packages()

        if not packages:
            return True  # Nothing to install

        r = self.get_session()

        # Create package list for R
        pkg_list = ', '.join([f'"{pkg}"' for pkg in packages])

        try:
            r(f'install.packages(c({pkg_list}), repos="https://cran.r-project.org", quiet=TRUE)')
            return True
        except Exception as e:
            print(f"Package installation error: {e}")
            return False

    def execute(self, r_code: str) -> Any:
        """
        Execute R code and return the result.

        Args:
            r_code: The R code to execute.

        Returns:
            The result of the R command execution.

        Raises:
            RuntimeError: If R is not available.
        """
        r = self.get_session()
        return r(r_code)

    def get(self, var_name: str) -> Any:
        """
        Get a variable from the R session.

        Args:
            var_name: The name of the R variable to retrieve.

        Returns:
            The value of the R variable.
        """
        r = self.get_session()
        return r.get(var_name)

    def assign(self, var_name: str, value: Any) -> None:
        """
        Assign a value to an R variable.

        Args:
            var_name: The name of the R variable.
            value: The value to assign.
        """
        r = self.get_session()
        r.assign(var_name, value)

    def load_library(self, library_name: str) -> bool:
        """
        Load an R library.

        Args:
            library_name: The name of the library to load.

        Returns:
            True if the library was loaded successfully, False otherwise.
        """
        try:
            r = self.get_session()
            r(f'library({library_name})')
            return True
        except:
            return False

    def close(self) -> None:
        """Close the R session and clean up resources."""
        if self._r_session is not None:
            try:
                # Clean up R session
                RSessionManager._r_session = None
            except:
                pass

    def get_r_version(self) -> Optional[str]:
        """
        Get the R version string.

        Returns:
            The R version string, or None if R is not available.
        """
        if not self._r_available:
            return None

        try:
            r = self.get_session()
            r('r_version <- R.version.string')
            return r.get('r_version')
        except:
            return None

    def get_status_message(self) -> str:
        """
        Get a human-readable status message about R availability.

        Returns:
            A string describing the current R status.
        """
        if not self._r_available:
            return (
                "R is not available.\n\n"
                "To enable R integration:\n"
                "1. Install R from https://cran.r-project.org/\n"
                "2. Add R to your system PATH\n"
                "3. Install PyPER: pip install pyper\n"
                "4. Restart QGIS"
            )

        version = self.get_r_version()
        missing = self.get_missing_packages()

        if missing:
            return (
                f"R is available ({version})\n\n"
                f"Missing packages: {', '.join(missing)}\n"
                "Click 'Install Packages' to install them."
            )

        return f"R is ready ({version})\nAll required packages are installed."
