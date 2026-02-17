"""
Rust acceleration module installer for PyArchInit.

Handles detection, download, and installation of the optional
pyarchinit_core Rust module from GitHub Releases.
"""

import os
import platform
import struct
import subprocess
import sys


def _get_python_executable():
    """Get the actual Python interpreter path, not the QGIS executable.

    In QGIS, sys.executable points to the QGIS binary, not Python.
    We need to find the actual Python interpreter for pip operations.
    """
    # Try common QGIS Python locations
    if sys.platform == 'darwin':
        # macOS: QGIS bundles Python in Frameworks
        for candidate in [
            os.path.join(sys.prefix, 'bin', 'python3'),
            os.path.join(sys.prefix, 'bin', 'python'),
            # Homebrew/conda
            os.path.join(os.path.dirname(sys.executable), 'python3'),
        ]:
            if os.path.isfile(candidate):
                return candidate
    elif sys.platform == 'win32':
        # Windows: QGIS bundles Python in apps/Python3x
        for candidate in [
            os.path.join(sys.prefix, 'python.exe'),
            os.path.join(os.path.dirname(sys.executable), 'python.exe'),
            os.path.join(sys.prefix, '..', 'apps', 'Python39', 'python.exe'),
            os.path.join(sys.prefix, '..', 'apps', 'Python311', 'python.exe'),
            os.path.join(sys.prefix, '..', 'apps', 'Python312', 'python.exe'),
        ]:
            candidate = os.path.normpath(candidate)
            if os.path.isfile(candidate):
                return candidate
    else:
        # Linux
        for candidate in [
            os.path.join(sys.prefix, 'bin', 'python3'),
            os.path.join(sys.prefix, 'bin', 'python'),
        ]:
            if os.path.isfile(candidate):
                return candidate

    # Fallback: check if sys.executable IS Python (not QGIS)
    try:
        result = subprocess.run(
            [sys.executable, '-c', 'import sys; print(sys.executable)'],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
    except Exception:
        pass

    return sys.executable


# GitHub release base URL
GITHUB_RELEASE_URL = (
    "https://github.com/pyarchinit/pyarchinit/releases/download"
)

# Default version to install when not specified
DEFAULT_VERSION = "0.1.0"


def check_rust_available():
    """Check if the Rust acceleration module is available.

    Returns:
        tuple: (available: bool, version: str or None)
    """
    try:
        import pyarchinit_core
        version = getattr(pyarchinit_core, '__version__', 'unknown')
        return True, version
    except ImportError:
        return False, None


def _get_platform_keywords():
    """Get keywords to match against wheel filenames for this platform.

    Returns:
        list[str]: Keywords that should appear in the wheel filename.
                   Returns empty list if platform is not supported.
    """
    system = platform.system()
    bits = struct.calcsize('P') * 8
    machine = platform.machine().lower()

    if system == 'Linux':
        if machine in ('x86_64', 'amd64') and bits == 64:
            return ['manylinux', 'x86_64']
        elif machine in ('aarch64', 'arm64') and bits == 64:
            return ['manylinux', 'aarch64']
    elif system == 'Darwin':
        # QGIS on macOS may run under Rosetta (x86_64 Python on arm64 Mac)
        import sysconfig
        plat = sysconfig.get_platform()
        if 'x86_64' in plat:
            # Prefer x86_64 or universal2
            return ['macosx']
        elif 'arm64' in plat:
            return ['macosx']
        return ['macosx']
    elif system == 'Windows':
        if machine in ('x86_64', 'amd64', 'x64') or bits == 64:
            return ['win_amd64']

    return []


def _build_wheel_url(version):
    """Find the correct wheel URL by querying the GitHub Release assets.

    Queries the GitHub Releases API to find the matching wheel for
    this platform, instead of guessing the exact filename.

    Args:
        version: Version string, e.g. '0.1.0'

    Returns:
        str: Full URL to the .whl file, or None if not found.
    """
    keywords = _get_platform_keywords()
    if not keywords:
        return None

    # Query GitHub API for release assets
    api_url = (
        f"https://api.github.com/repos/pyarchinit/pyarchinit"
        f"/releases/tags/rust-v{version}"
    )

    try:
        import urllib.request
        import json
        req = urllib.request.Request(api_url)
        req.add_header('Accept', 'application/vnd.github.v3+json')
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode())
    except Exception as e:
        print(f"[PyArchInit] Failed to query GitHub API: {e}")
        return None

    # Find matching wheel among release assets
    for asset in data.get('assets', []):
        name = asset.get('name', '')
        if not name.endswith('.whl'):
            continue
        if not name.startswith('pyarchinit_core'):
            continue
        # Check all keywords match
        if all(kw in name for kw in keywords):
            return asset.get('browser_download_url')

    print(
        f"[PyArchInit] No matching wheel found for platform "
        f"keywords={keywords}"
    )
    return None


def install_rust_acceleration(version=None):
    """Download and install the Rust acceleration module.

    Args:
        version: Version to install. Defaults to DEFAULT_VERSION.

    Returns:
        tuple: (success: bool, message: str)
    """
    if version is None:
        version = DEFAULT_VERSION

    wheel_url = _build_wheel_url(version)
    if wheel_url is None:
        system = platform.system()
        machine = platform.machine()
        msg = (f"No matching wheel for {system}/{machine}. "
               f"Check GitHub Releases for rust-v{version}.")
        print(f"[PyArchInit] {msg}")
        return False, msg

    print(f"[PyArchInit] Installing Rust acceleration from: {wheel_url}")

    try:
        python_exe = _get_python_executable()
        print(f"[PyArchInit] Using Python: {python_exe}")
        result = subprocess.run(
            [python_exe, '-m', 'pip', 'install', '--force-reinstall',
             wheel_url],
            capture_output=True,
            text=True,
            timeout=120
        )
        if result.returncode == 0:
            msg = f"v{version} installed from {wheel_url}"
            print(f"[PyArchInit] {msg}")
            # Reset the bridge so it re-checks on next use
            try:
                from modules._rust_bridge import rust_bridge
                rust_bridge._checked = False
                rust_bridge._available = False
                rust_bridge._module = None
            except Exception:
                pass
            return True, msg
        else:
            stderr = result.stderr.strip()
            stdout = result.stdout.strip()
            msg = stderr or stdout or "pip returned non-zero exit code"
            print(f"[PyArchInit] Install failed: {msg}")
            return False, msg
    except subprocess.TimeoutExpired:
        msg = "Download/install timed out after 120s"
        print(f"[PyArchInit] {msg}")
        return False, msg
    except Exception as e:
        msg = str(e)
        print(f"[PyArchInit] Install error: {msg}")
        return False, msg
