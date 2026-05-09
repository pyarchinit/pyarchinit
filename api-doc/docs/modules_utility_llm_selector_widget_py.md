# modules/utility/llm_selector_widget.py

## Overview

This file contains 7 documented elements.

## Classes

### LLMSelectorWidget

Reusable provider/model picker.

Signals:
    config_changed(LLMConfig): emitted whenever provider, model or key
        changes. Connect to this if you want to react in real time.

**Inherits from**: QWidget

#### Methods

##### __init__(self, parent, scope, vision_only, title)

Initializes a new instance of the AI provider configuration widget, setting up its core state and user interface.

Accepts an optional parent widget, a `scope` string (defaulting to `"default"`), a `vision_only` boolean flag, and a `title` string (defaulting to `"Provider AI"`). Stores the provided arguments as instance attributes, initializes `_discovery_thread` and `_loading` to `None` and `False` respectively, then delegates to `_setup_ui` to build the interface and `_load_saved_config` to restore any previously saved configuration.

##### get_config(self)

*No description available.*
Reads the current state of the UI controls and constructs an `LLMConfig` instance reflecting the selected provider and model. If the selected provider requires an API key (as determined by `PROVIDER_DEFAULTS`), the key is retrieved from the `api_key_edit` field or, as a fallback, from `LLMProviderManager.get_api_key`. Returns the resulting `LLMConfig` object populated with the resolved `provider`, `model`, and `api_key` values.

##### set_provider(self, provider)

Programmatically switch provider (also persists).

