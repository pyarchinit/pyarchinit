# modules/geoarchaeo/gui/main_dock.py

## Overview

This file contains 11 documented elements.

## Classes

### AnalysisThread

Thread per analisi pesanti - versione robusta

**Inherits from**: QThread

#### Methods

##### __init__(self, engine, method, params)

Initializes a new worker thread instance by calling the parent class constructor and storing the provided `engine`, `method`, and `params` arguments as instance attributes. Sets the `_is_cancelled` flag to `False`, indicating the thread has not been requested to cancel at the time of creation.

##### cancel(self)

Request thread cancellation

##### run(self)

Esegue analisi nel thread con protezione massima

### GeoArchaeoDockWidget

Widget principale del plugin

**Inherits from**: QDockWidget

#### Methods

##### __init__(self, parent)

Initializes the `GeoArchaeo Analysis` panel by calling the parent constructor with the title `"GeoArchaeo Analysis"` and constructing the full UI layout within a `QWidget`. Sets up a `QVBoxLayout` containing a toolbar, a `QTabWidget` with six tabs (data, variogram, kriging, ML, sampling, and report), and a hidden `QProgressBar`. Also instantiates a `GeostatEngine`, initializes `analysis_thread` to `None`, sets `current_results` to an empty dictionary, and builds a `_tab_indices` mapping for both English and Italian tab name variants.

##### switch_to_tab(self, tab_name)

Switch to a specific tab by name

##### generate_full_report(self)

Generate full report - called from plugin menu

## Functions

### log(msg)

*No description available.*
Appends a timestamped message to a log file located at `~/Desktop/geoarchaeo_kriging_log.txt`. Each entry is prefixed with the label `THREAD` followed by the current time formatted as `HH:MM:SS.ffffff`, and terminated with a newline character. All file write errors are silently suppressed.

**Parameters:**
- `msg`

### log(msg)

*No description available.*
Appends a timestamped message to a log file located at `~/Desktop/geoarchaeo_kriging_log.txt`. Each entry is prefixed with `[COMPLETE HH:MM:SS.ffffff]` using the current local time, followed by the provided message and a newline character. If any exception occurs during the write operation, it is silently suppressed.

**Parameters:**
- `msg`

