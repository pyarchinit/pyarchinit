#!/usr/bin/env python3
"""
Test script for Unibo File Manager Storage Backend
===================================================

This script tests the connection and basic operations with the
University of Bologna File Manager from PyArchInit.

Usage:
    python test_unibo_storage.py

Author: Enzo Cocca
"""

import sys
import os

# Add the modules path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.storage import StorageManager
from modules.storage.credentials import CredentialsManager


def test_unibo_backend():
    """Test the Unibo File Manager backend"""

    print("=" * 60)
    print("Test Unibo File Manager Storage Backend")
    print("=" * 60)

    # Configuration - UPDATE THESE VALUES
    SERVER_URL = "https://137.204.128.220"
    USERNAME = "enzo.cocca@unibo.it"
    PASSWORD = "Baselice@80"  # In production, use environment variables!
    PROJECT_CODE = "Al-Khutm"
    FOLDER_PATH = "KTM2025/photolog/original"

    # Build the unibo:// URL
    storage_path = f"unibo://{PROJECT_CODE}/{FOLDER_PATH}"
    print(f"\nStorage path: {storage_path}")

    # Create credentials
    credentials = {
        'username': USERNAME,
        'password': PASSWORD,
        'server_url': SERVER_URL
    }

    # Create storage manager
    storage = StorageManager()

    # Import and register the Unibo backend
    from modules.storage.unibo_filemanager_backend import UniboFileManagerBackend
    from modules.storage.base_backend import StorageType
    storage.register_backend(StorageType.UNIBO, UniboFileManagerBackend)

    print("\n1. Creating backend...")
    try:
        # Get backend with credentials
        from modules.storage.unibo_filemanager_backend import UniboFileManagerBackend
        backend = UniboFileManagerBackend(
            base_path=f"{PROJECT_CODE}/{FOLDER_PATH}",
            credentials=credentials
        )
        print("   Backend created successfully")
    except Exception as e:
        print(f"   ERROR: Failed to create backend: {e}")
        return False

    print("\n2. Connecting to server...")
    try:
        if backend.connect():
            print("   Connected successfully!")
            print(f"   Project ID: {backend._project_id}")
            print(f"   Folder ID: {backend._folder_id}")
        else:
            print("   ERROR: Connection failed")
            return False
    except Exception as e:
        print(f"   ERROR: Connection error: {e}")
        return False

    print("\n3. Listing files...")
    try:
        files = backend.list()
        print(f"   Found {len(files)} items:")
        for f in files[:10]:  # Show first 10
            type_str = "[DIR] " if f.is_directory else "[FILE]"
            size_str = f" ({f.size} bytes)" if not f.is_directory else ""
            print(f"   {type_str} {f.name}{size_str}")
        if len(files) > 10:
            print(f"   ... and {len(files) - 10} more")
    except Exception as e:
        print(f"   ERROR: Failed to list files: {e}")

    print("\n4. Testing file existence...")
    try:
        if files:
            # Find a file (not directory) to test
            test_file = None
            for f in files:
                if not f.is_directory:
                    test_file = f.name
                    break

            if test_file:
                exists = backend.exists(test_file)
                print(f"   File '{test_file}' exists: {exists}")
            else:
                print("   No files found to test")
    except Exception as e:
        print(f"   ERROR: Failed to check file existence: {e}")

    print("\n5. Testing file URL...")
    try:
        if test_file:
            url = backend.get_url(test_file)
            print(f"   URL for '{test_file}':")
            print(f"   {url}")
    except Exception as e:
        print(f"   ERROR: Failed to get file URL: {e}")

    print("\n6. Disconnecting...")
    backend.disconnect()
    print("   Disconnected")

    print("\n" + "=" * 60)
    print("Test completed successfully!")
    print("=" * 60)

    return True


if __name__ == "__main__":
    success = test_unibo_backend()
    sys.exit(0 if success else 1)
