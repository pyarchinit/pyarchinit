"""
Credentials Manager
===================

Secure storage and management of credentials for remote storage backends.
Supports multiple credential sources:
- Environment variables
- .env files
- QGIS settings
- Encrypted credential store

Author: PyArchInit Team
License: GPL v2
"""

import os
import json
from typing import Optional, Dict, Any
from pathlib import Path
from dataclasses import dataclass, field
from enum import Enum

from .base_backend import StorageType


class CredentialSource(Enum):
    """Where credentials can be loaded from"""
    ENVIRONMENT = "environment"
    ENV_FILE = "env_file"
    QGIS_SETTINGS = "qgis_settings"
    JSON_FILE = "json_file"
    MANUAL = "manual"


@dataclass
class StorageCredentials:
    """Container for storage credentials"""
    storage_type: StorageType
    source: CredentialSource
    data: Dict[str, Any] = field(default_factory=dict)

    def get(self, key: str, default: Any = None) -> Any:
        """Get a credential value"""
        return self.data.get(key, default)

    def __getitem__(self, key: str) -> Any:
        return self.data[key]

    def __contains__(self, key: str) -> bool:
        return key in self.data


class CredentialsManager:
    """
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
    """

    # Environment variable prefix
    ENV_PREFIX = "PYARCHINIT_"

    # Mapping of storage types to their required credentials
    REQUIRED_CREDENTIALS = {
        StorageType.GOOGLE_DRIVE: ['client_id', 'client_secret'],
        StorageType.DROPBOX: ['access_token'],
        StorageType.S3: ['access_key', 'secret_key', 'region'],
        StorageType.R2: ['access_key', 'secret_key', 'account_id'],
        StorageType.WEBDAV: ['username', 'password'],
        StorageType.HTTP: [],  # May be empty for public URLs
        StorageType.SFTP: ['username'],  # Password or key
        StorageType.CLOUDINARY: ['cloud_name', 'api_key', 'api_secret'],
    }

    # Environment variable names for each storage type
    ENV_NAMES = {
        StorageType.GOOGLE_DRIVE: {
            'client_id': 'GDRIVE_CLIENT_ID',
            'client_secret': 'GDRIVE_CLIENT_SECRET',
            'refresh_token': 'GDRIVE_REFRESH_TOKEN',
        },
        StorageType.DROPBOX: {
            'access_token': 'DROPBOX_TOKEN',
            'app_key': 'DROPBOX_APP_KEY',
            'app_secret': 'DROPBOX_APP_SECRET',
        },
        StorageType.S3: {
            'access_key': 'S3_ACCESS_KEY',
            'secret_key': 'S3_SECRET_KEY',
            'region': 'S3_REGION',
            'endpoint': 'S3_ENDPOINT',
        },
        StorageType.R2: {
            'access_key': 'R2_ACCESS_KEY',
            'secret_key': 'R2_SECRET_KEY',
            'account_id': 'R2_ACCOUNT_ID',
        },
        StorageType.WEBDAV: {
            'username': 'WEBDAV_USERNAME',
            'password': 'WEBDAV_PASSWORD',
        },
        StorageType.HTTP: {
            'username': 'HTTP_USERNAME',
            'password': 'HTTP_PASSWORD',
            'bearer_token': 'HTTP_BEARER_TOKEN',
            'api_key': 'HTTP_API_KEY',
        },
        StorageType.SFTP: {
            'username': 'SFTP_USERNAME',
            'password': 'SFTP_PASSWORD',
            'private_key': 'SFTP_PRIVATE_KEY',
            'private_key_path': 'SFTP_PRIVATE_KEY_PATH',
        },
        StorageType.CLOUDINARY: {
            'cloud_name': 'CLOUDINARY_CLOUD_NAME',
            'api_key': 'CLOUDINARY_API_KEY',
            'api_secret': 'CLOUDINARY_API_SECRET',
            'folder': 'CLOUDINARY_FOLDER',
            'auto_tagging': 'CLOUDINARY_AUTO_TAGGING',
        },
    }

    def __init__(self, plugin_path: Optional[str] = None):
        """
        Initialize the credentials manager.

        Args:
            plugin_path: Path to the plugin directory for .env file lookup
        """
        self.plugin_path = plugin_path
        self._manual_credentials: Dict[StorageType, Dict[str, Any]] = {}
        self._cached_credentials: Dict[StorageType, StorageCredentials] = {}
        self._env_loaded = False

    def _get_plugin_path(self) -> Path:
        """Get the plugin directory path"""
        if self.plugin_path:
            return Path(self.plugin_path)

        # Try to detect plugin path
        current_file = Path(__file__)
        # Go up from modules/storage/credentials.py to plugin root
        return current_file.parent.parent.parent

    def _load_env_file(self):
        """Load environment variables from .env file"""
        if self._env_loaded:
            return

        env_file = self._get_plugin_path() / '.env'
        if env_file.exists():
            try:
                with open(env_file, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            key, value = line.split('=', 1)
                            key = key.strip()
                            value = value.strip().strip('"\'')
                            if key not in os.environ:
                                os.environ[key] = value
            except Exception:
                pass

        self._env_loaded = True

    def _load_from_environment(self, storage_type: StorageType) -> Dict[str, Any]:
        """Load credentials from environment variables"""
        self._load_env_file()

        credentials = {}
        env_names = self.ENV_NAMES.get(storage_type, {})

        for cred_key, env_name in env_names.items():
            full_env_name = f"{self.ENV_PREFIX}{env_name}"
            value = os.environ.get(full_env_name)
            if value:
                credentials[cred_key] = value

        return credentials

    def _load_from_qgis_settings(self, storage_type: StorageType) -> Dict[str, Any]:
        """Load credentials from QGIS settings"""
        credentials = {}

        try:
            from qgis.core import QgsSettings
            settings = QgsSettings()

            prefix = f"pyarchinit/storage/{storage_type.value}/"
            env_names = self.ENV_NAMES.get(storage_type, {})

            for cred_key in env_names.keys():
                value = settings.value(f"{prefix}{cred_key}", None)
                if value:
                    credentials[cred_key] = value

        except ImportError:
            # QGIS not available
            pass

        return credentials

    def _load_from_json_file(self, storage_type: StorageType) -> Dict[str, Any]:
        """Load credentials from JSON file"""
        credentials = {}

        json_file = self._get_plugin_path() / 'storage_credentials.json'
        if json_file.exists():
            try:
                with open(json_file, 'r') as f:
                    all_creds = json.load(f)
                    credentials = all_creds.get(storage_type.value, {})
            except (json.JSONDecodeError, IOError):
                pass

        return credentials

    def get_credentials(self, storage_type: StorageType) -> Optional[Dict[str, Any]]:
        """
        Get credentials for a storage type.

        Credentials are loaded from multiple sources in priority order.

        Args:
            storage_type: The storage type to get credentials for

        Returns:
            Dictionary of credentials, or None if not available
        """
        # Check cache
        if storage_type in self._cached_credentials:
            return self._cached_credentials[storage_type].data

        credentials = {}
        source = CredentialSource.ENVIRONMENT

        # Load from different sources (in order of priority, later sources override)

        # 1. JSON file (lowest priority)
        json_creds = self._load_from_json_file(storage_type)
        if json_creds:
            credentials.update(json_creds)
            source = CredentialSource.JSON_FILE

        # 2. QGIS settings
        qgis_creds = self._load_from_qgis_settings(storage_type)
        if qgis_creds:
            credentials.update(qgis_creds)
            source = CredentialSource.QGIS_SETTINGS

        # 3. Environment variables (including .env file)
        env_creds = self._load_from_environment(storage_type)
        if env_creds:
            credentials.update(env_creds)
            source = CredentialSource.ENVIRONMENT

        # 4. Manual credentials (highest priority)
        if storage_type in self._manual_credentials:
            credentials.update(self._manual_credentials[storage_type])
            source = CredentialSource.MANUAL

        if credentials:
            self._cached_credentials[storage_type] = StorageCredentials(
                storage_type=storage_type,
                source=source,
                data=credentials
            )
            return credentials

        return None

    def set_credentials(self, storage_type: StorageType, credentials: Dict[str, Any]):
        """
        Set credentials manually (highest priority).

        Args:
            storage_type: The storage type
            credentials: Dictionary of credentials
        """
        self._manual_credentials[storage_type] = credentials
        # Invalidate cache
        if storage_type in self._cached_credentials:
            del self._cached_credentials[storage_type]

    def save_to_qgis_settings(self, storage_type: StorageType, credentials: Dict[str, Any]):
        """
        Save credentials to QGIS settings.

        Args:
            storage_type: The storage type
            credentials: Dictionary of credentials to save
        """
        try:
            from qgis.core import QgsSettings
            settings = QgsSettings()

            prefix = f"pyarchinit/storage/{storage_type.value}/"

            for key, value in credentials.items():
                settings.setValue(f"{prefix}{key}", value)

            # Invalidate cache
            if storage_type in self._cached_credentials:
                del self._cached_credentials[storage_type]

        except ImportError:
            raise RuntimeError("QGIS not available for saving settings")

    def save_to_json_file(self, storage_type: StorageType, credentials: Dict[str, Any]):
        """
        Save credentials to JSON file.

        WARNING: This stores credentials in plain text. Use only for development.

        Args:
            storage_type: The storage type
            credentials: Dictionary of credentials to save
        """
        json_file = self._get_plugin_path() / 'storage_credentials.json'

        # Load existing credentials
        all_creds = {}
        if json_file.exists():
            try:
                with open(json_file, 'r') as f:
                    all_creds = json.load(f)
            except (json.JSONDecodeError, IOError):
                pass

        # Update credentials for this storage type
        all_creds[storage_type.value] = credentials

        # Save back
        with open(json_file, 'w') as f:
            json.dump(all_creds, f, indent=2)

        # Invalidate cache
        if storage_type in self._cached_credentials:
            del self._cached_credentials[storage_type]

    def clear_cache(self):
        """Clear the credentials cache"""
        self._cached_credentials.clear()

    def has_credentials(self, storage_type: StorageType) -> bool:
        """
        Check if credentials are available for a storage type.

        Args:
            storage_type: The storage type to check

        Returns:
            True if credentials are available
        """
        creds = self.get_credentials(storage_type)
        if not creds:
            return False

        # Check if required credentials are present
        required = self.REQUIRED_CREDENTIALS.get(storage_type, [])
        return all(key in creds for key in required)

    def get_missing_credentials(self, storage_type: StorageType) -> list:
        """
        Get list of missing required credentials.

        Args:
            storage_type: The storage type to check

        Returns:
            List of missing credential keys
        """
        creds = self.get_credentials(storage_type) or {}
        required = self.REQUIRED_CREDENTIALS.get(storage_type, [])
        return [key for key in required if key not in creds]
