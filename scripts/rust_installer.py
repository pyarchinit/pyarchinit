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


def _get_wheel_tag():
    """Determine the correct wheel tag for the current platform/arch.

    Returns:
        str: The wheel platform tag (e.g. 'manylinux_2_17_x86_64',
             'macosx_11_0_universal2', 'win_amd64'), or None if
             the platform is not supported.
    """
    system = platform.system()
    # Detect architecture: 64-bit pointer size and machine name
    bits = struct.calcsize('P') * 8
    machine = platform.machine().lower()

    if system == 'Linux':
        if machine in ('x86_64', 'amd64') and bits == 64:
            return 'manylinux_2_17_x86_64.manylinux2014_x86_64'
        elif machine in ('aarch64', 'arm64') and bits == 64:
            return 'manylinux_2_17_aarch64.manylinux2014_aarch64'
    elif system == 'Darwin':
        # Universal2 binary works on both Intel and Apple Silicon
        return 'macosx_11_0_universal2'
    elif system == 'Windows':
        if machine in ('x86_64', 'amd64', 'x64') or bits == 64:
            return 'win_amd64'

    return None


def _build_wheel_url(version):
    """Build the full wheel download URL for the current platform.

    Args:
        version: Version string, e.g. '0.1.0'

    Returns:
        str: Full URL to the .whl file, or None if platform not supported.
    """
    wheel_tag = _get_wheel_tag()
    if wheel_tag is None:
        return None

    wheel_filename = (
        f"pyarchinit_core-{version}-cp39-abi3-{wheel_tag}.whl"
    )
    return f"{GITHUB_RELEASE_URL}/rust-v{version}/{wheel_filename}"


def install_rust_acceleration(version=None):
    """Download and install the Rust acceleration module.

    Args:
        version: Version to install. Defaults to DEFAULT_VERSION.

    Returns:
        bool: True if installation succeeded, False otherwise.
    """
    if version is None:
        version = DEFAULT_VERSION

    wheel_url = _build_wheel_url(version)
    if wheel_url is None:
        system = platform.system()
        machine = platform.machine()
        print(
            f"[PyArchInit] Rust acceleration: unsupported platform "
            f"{system}/{machine}"
        )
        return False

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
            print("[PyArchInit] Rust acceleration installed successfully")
            # Reset the bridge so it re-checks on next use
            try:
                from modules._rust_bridge import rust_bridge
                rust_bridge._checked = False
                rust_bridge._available = False
                rust_bridge._module = None
            except Exception:
                pass
            return True
        else:
            print(
                f"[PyArchInit] Rust acceleration install failed: "
                f"{result.stderr}"
            )
            return False
    except subprocess.TimeoutExpired:
        print("[PyArchInit] Rust acceleration install timed out")
        return False
    except Exception as e:
        print(f"[PyArchInit] Rust acceleration install error: {e}")
        return False
