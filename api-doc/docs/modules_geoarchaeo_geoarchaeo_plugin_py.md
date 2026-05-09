# modules/geoarchaeo/geoarchaeo_plugin.py

## Overview

This file contains 12 documented elements.

## Classes

### GeoArchaeoPlugin

Plugin QGIS per analisi geostatistica archeologica avanzata

#### Methods

##### __init__(self, iface)

Initializes a new `GeoArchaeoPlugin` instance by storing the provided QGIS interface object (`iface`) and resolving the plugin's directory path from the current file location. Sets up instance attributes including `provider`, `dock`, `toolbar`, `actions`, `menu`, and instantiates the `GeostatEngine` assigned to `self.engine`. All GUI-related components (`provider`, `dock`, `toolbar`) are initialized to `None` and `actions` to an empty list, with full GUI setup deferred to `initGui`.

##### initGui(self)

Inizializza interfaccia plugin

##### toggle_dock(self)

Mostra/nascondi dock widget

##### quick_variogram(self)

Lancia analisi variogramma rapida

##### quick_kriging(self)

Lancia kriging rapido

##### ml_analysis(self)

Lancia analisi Machine Learning

##### generate_report(self)

Genera report completo

##### show_help(self)

Mostra guida HTML

##### load_test_layers(self)

Carica layer di test

##### unload(self)

Rimuove il plugin

