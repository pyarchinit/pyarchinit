# modules/utility/askgpt.py

## Overview

This file contains 5 documented elements.

## Classes

### MyApp

*No description available.*
A `QWidget` subclass that provides LLM (Large Language Model) integration within a Qt-based GUI application. It exposes two prompt-submission methods — `ask_gpt` (a backward-compatible OpenAI-specific wrapper) and `ask_with_config` (a provider-agnostic interface accepting an `LLMConfig` object) — both of which return the full text response or `None` on error, displaying error details via `QMessageBox`. The class also includes an `is_connected` utility method that checks network connectivity by attempting a socket connection to `1.1.1.1` on port 53.

**Inherits from**: QWidget

#### Methods

##### __init__(self, parent)

*No description available.*
Initializes the `MyApp` widget instance by delegating to the parent class constructor via `super().__init__(parent)`. Accepts a `parent` parameter that is passed directly to the `QWidget` base class initializer.

##### ask_gpt(self, prompt, apikey, model)

Backward-compatible OpenAI wrapper.

New code should prefer ``ask_with_config`` which supports any provider.

##### ask_with_config(self, prompt, config)

Send a single prompt to the configured LLM provider.

Returns the full text response, or None on error.

##### is_connected(self)

*No description available.*
Checks whether a network connection is available by attempting to establish a TCP connection to `1.1.1.1` on port 53. Returns `True` if the connection succeeds, or `False` if an `OSError` is raised during the attempt.

