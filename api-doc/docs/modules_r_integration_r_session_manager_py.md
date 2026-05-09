# modules/r_integration/r_session_manager.py

## Overview

This file contains 17 documented elements.

## Classes

### RSessionManager

Singleton class for managing R session lifecycle.

Provides methods to:
- Check R availability
- Initialize and manage R sessions
- Check and install required R packages
- Execute R code safely

#### Methods

##### __new__(cls)

Singleton pattern implementation.

##### get_instance(cls)

Get the singleton instance of RSessionManager.

##### __init__(self)

Initialize the R session manager.

##### is_available(self)

Check if R is available for use.

Returns:
    True if R is installed and PyPER can connect to it, False otherwise.

##### get_session(self)

Get the R session, creating one if necessary.

Returns:
    The R session object from PyPER.

Raises:
    RuntimeError: If R is not available.

##### check_packages(self)

Check which required R packages are installed.

Returns:
    Dictionary mapping package names to their installation status.

##### get_missing_packages(self)

Get list of required packages that are not installed.

Returns:
    List of package names that need to be installed.

##### install_packages(self, packages)

Install R packages from CRAN.

Args:
    packages: List of package names to install.
              If None, installs all missing required packages.

Returns:
    True if installation was attempted, False if R is not available.

##### execute(self, r_code)

Execute R code and return the result.

Args:
    r_code: The R code to execute.

Returns:
    The result of the R command execution.

Raises:
    RuntimeError: If R is not available.

##### get(self, var_name)

Get a variable from the R session.

Args:
    var_name: The name of the R variable to retrieve.

Returns:
    The value of the R variable.

##### assign(self, var_name, value)

Assign a value to an R variable.

Args:
    var_name: The name of the R variable.
    value: The value to assign.

##### load_library(self, library_name)

Load an R library.

Args:
    library_name: The name of the library to load.

Returns:
    True if the library was loaded successfully, False otherwise.

##### close(self)

Close the R session and clean up resources.

##### get_r_version(self)

Get the R version string.

Returns:
    The R version string, or None if R is not available.

##### get_status_message(self)

Get a human-readable status message about R availability.

Returns:
    A string describing the current R status.

