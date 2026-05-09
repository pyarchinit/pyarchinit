# modules/utility/llm_providers.py

## Overview

This file contains 20 documented elements.

## Classes

### LLMProvider

*No description available.*
An enumeration that identifies supported large language model (LLM) backend providers. Defines four members — `OPENAI`, `ANTHROPIC`, `OLLAMA`, and `LMSTUDIO` — each mapped to its corresponding string identifier. Used as a key type in provider configuration structures such as `PROVIDER_DEFAULTS`.

**Inherits from**: Enum

### LLMConfig

*No description available.*
A dataclass that holds configuration parameters for a large language model provider, including the provider type, model identifier, API key, base URL, and an optional dictionary of extra settings. On initialization, if `base_url` is not explicitly provided, it is automatically populated from the `PROVIDER_DEFAULTS` mapping for the given provider. Exposes two read-only properties, `is_local` and `needs_api_key`, which reflect provider-level defaults from the same `PROVIDER_DEFAULTS` mapping.

**Decorators**: dataclass

#### Methods

##### __post_init__(self)

Sets `base_url` to the provider's default value from `PROVIDER_DEFAULTS` if `base_url` was not supplied at initialization. This method is automatically invoked by the dataclass machinery immediately after `__init__` completes.

##### is_local(self)

*No description available.*
**Type:** `property` → `bool`

Returns whether the current provider is a local provider, as defined by the `"is_local"` key in `PROVIDER_DEFAULTS` for the configured `provider`. This value is looked up directly from the `PROVIDER_DEFAULTS` mapping and reflects a static configuration associated with the provider. No computation or external calls are performed beyond the dictionary lookup.

##### needs_api_key(self)

*No description available.*
**Type:** `property` → `bool`

Indicates whether the current provider requires an API key for authentication. Returns the `"needs_api_key"` value from the `PROVIDER_DEFAULTS` configuration dictionary for the associated provider. This property can be used to determine whether API key handling is necessary before interacting with the provider.

### LLMProviderManager

*No description available.*
A static utility class that centralises all interactions with LLM providers (OpenAI, Anthropic, Ollama, and LM Studio). It handles provider availability checks, model discovery, chat client construction, streaming and non-streaming inference, API key persistence to provider-specific files, and configuration persistence to QSettings under the `"pyArchInit/llm/"` prefix. All public methods are static; the class constant `SETTINGS_PREFIX = "pyArchInit/llm/"` defines the QSettings namespace used by `save_config` and `load_config`.

#### Methods

##### is_provider_available(provider, timeout)

Health check.

Cloud providers always return True (we can only know once we make a real
call). Local providers do a fast TCP connect to ``host:port``.

##### discover_models(provider, timeout)

Return the list of usable model IDs on the provider.

- **LM Studio**: prefers the native ``/api/v0/models`` endpoint and
  returns only models with ``state == "loaded"`` — calling chat with
  a model that's merely *downloaded* (not loaded into RAM) returns a
  400 "No models loaded" error.
- **Ollama**: returns all installed models (Ollama lazy-loads on
  first use, so any installed model is usable).
- **OpenAI / Anthropic**: returns a curated default list (the cloud
  ``/models`` endpoints either require auth or report hundreds of
  irrelevant entries).

##### discover_embedding_models(provider, timeout)

Return loaded embedding model IDs on a local provider.

Used by ``_get_embeddings`` to decide whether the chosen local server
can serve ``/v1/embeddings`` calls — if not, callers should fall back
to OpenAI cloud embeddings (whose vectors only need to be consistent
within the FAISS index, not aligned with the chat model).

##### discover_all_models(provider, timeout)

Return *all* models on a local provider with metadata.

Each entry is ``{"id": str, "loaded": bool, "type": str}`` where
``type`` is ``"llm" / "vlm" / "embeddings"`` when reported by the
backend, or ``""`` otherwise. Only meaningful for LM Studio (which
distinguishes loaded vs downloaded). For Ollama all installed models
are reported as loaded since Ollama auto-loads on demand.

##### filter_vision_models(provider, models)

Best-effort filter to keep only models likely to support images.

##### get_chat_client(config)

Factory returning a configured client.

OpenAI / Ollama / LM Studio share the ``openai.OpenAI`` client.
Anthropic uses the dedicated ``anthropic.Anthropic`` client.

##### stream_chat(config, messages, max_tokens, temperature)

Unified streaming generator yielding text chunks.

Hides the Anthropic vs OpenAI streaming API difference. ``messages``
follows the OpenAI shape ``[{"role": "system"|"user"|"assistant",
"content": "..."}]``; for Anthropic the system message is extracted
and passed via ``system=`` (Anthropic's required convention).

##### chat(config, messages, max_tokens, temperature)

Non-streaming convenience wrapper. Concatenates all chunks.

##### get_api_key(provider)

Read the saved API key for cloud providers (empty for local).

##### save_api_key(provider, key)

Persists the API key for the specified `LLMProvider` to a file on disk. If the provider is marked as local in `PROVIDER_DEFAULTS`, the method returns immediately without writing anything. Otherwise, it resolves the key file path via `_key_file_path`, creates any missing parent directories, and writes the stripped key string to the file.

##### save_config(config, scope)

Persist config (provider, model, base_url) to QSettings.

API keys are NOT saved here — they live in the dedicated key files.

##### load_config(scope)

Loads and returns an `LLMConfig` instance from `QSettings` for the specified scope. It reads the provider, model, and base URL values stored under the corresponding settings prefix; if no provider value is found or the value cannot be mapped to a valid `LLMProvider`, the method returns `None`. If the resulting configuration requires an API key, it is retrieved via `LLMProviderManager.get_api_key` and assigned before the config is returned.

##### resolve_config(scope, fallback_provider)

Return the saved config for ``scope``, or a sensible default.

This is the single entry point callers should use when they just want
"the AI config the user picked".

