# modules/storage/credentials.py

## Overview

This file contains 15 documented elements.

## Classes

### CredentialSource

Where credentials can be loaded from

**Inherits from**: Enum

### StorageCredentials

Container for storage credentials

**Decorators**: dataclass

#### Methods

##### get(self, key, default)

Get a credential value

##### __getitem__(self, key)

*No description available.*
Enables bracket-notation access to credential values by delegating to the underlying `data` mapping. Accepts a string `key` and returns the corresponding value from `self.data`. Raises a `KeyError` if the specified key does not exist in `self.data`.

##### __contains__(self, key)

*No description available.*
Implements the `in` membership test operator for the containing class. Returns `True` if the given `key` exists in `self.data`, and `False` otherwise. This allows callers to check for key presence using standard Python `in` syntax.

### CredentialsManager

Manages credentials for storage backends.

Credentials are loaded in order of priority:
1. Manual credentials (set programmatically)
2. Environment variables
3. .env file in plugin directory
4. QGIS settings
5. JSON credential file

Environment variable naming convention:
- PYARCHINIT_GDRIVE_CLIENT_ID
- PYARCHINIT_GDRIVE_CLIENT_SECRET
- PYARCHINIT_DROPBOX_TOKEN
- PYARCHINIT_S3_ACCESS_KEY
- PYARCHINIT_S3_SECRET_KEY
- etc.

#### Methods

##### __init__(self, plugin_path)

Initialize the credentials manager.

Args:
    plugin_path: Path to the plugin directory for .env file lookup

##### get_credentials(self, storage_type)

Get credentials for a storage type.

Credentials are loaded from multiple sources in priority order.

Args:
    storage_type: The storage type to get credentials for

Returns:
    Dictionary of credentials, or None if not available

##### set_credentials(self, storage_type, credentials)

Set credentials manually (highest priority).

Args:
    storage_type: The storage type
    credentials: Dictionary of credentials

##### save_to_qgis_settings(self, storage_type, credentials)

Save credentials to QGIS settings.

Args:
    storage_type: The storage type
    credentials: Dictionary of credentials to save

##### save_to_json_file(self, storage_type, credentials)

Save credentials to JSON file.

WARNING: This stores credentials in plain text. Use only for development.

Args:
    storage_type: The storage type
    credentials: Dictionary of credentials to save

##### clear_cache(self)

Clear the credentials cache

##### has_credentials(self, storage_type)

Check if credentials are available for a storage type.

Args:
    storage_type: The storage type to check

Returns:
    True if credentials are available

##### get_missing_credentials(self, storage_type)

Get list of missing required credentials.

Args:
    storage_type: The storage type to check

Returns:
    List of missing credential keys

