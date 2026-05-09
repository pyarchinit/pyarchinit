# modules/utility/settings.py

## Overview

This file contains 4 documented elements.

## Classes

### Settings

## `Settings` class

Manages application configuration for the pyarchinit QGIS plugin by reading and parsing a `config.cfg` file located under the `PYARCHINIT_HOME` environment directory. At class definition time, it ensures that required configuration keys (`THUMB_RESIZE`, `SITE_SET`, `LOGO`, and `SSLMODE`) are present in the configuration file, appending missing entries with default placeholder values. The `__init__` method accepts a raw string and evaluates it as a Python dictionary, while `set_configuration` populates the instance attributes (`SERVER`, `HOST`, `DATABASE`, `PASSWORD`, `PORT`, `USER`, `SSLMODE`, `THUMB_PATH`, `THUMB_RESIZE`, `SITE_SET`, and `LOGO`) from that parsed dictionary.

**Inherits from**: object

#### Methods

##### __init__(self, s)

*No description available.*
Initializes a new instance of the class by evaluating the string parameter `s` and storing the result in the `configuration` instance attribute. The parameter `s` is expected to be a string representation of a Python object (such as a dictionary) that can be processed by `eval`.

##### set_configuration(self)

Reads values from the `self.configuration` dictionary and assigns them to corresponding instance attributes: `SERVER`, `HOST`, `DATABASE`, `PASSWORD`, `PORT`, `USER`, `THUMB_PATH`, `THUMB_RESIZE`, `SITE_SET`, and `LOGO`. The `SSLMODE` attribute is set using `dict.get` with a default value of `'allow'` if the key is not present in the configuration. Additionally, a local variable `PLUGIN_PATH` is set to the directory path of the current file using `os.path.dirname(__file__)`.

