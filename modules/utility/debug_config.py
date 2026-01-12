#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Debug configuration for PyArchInit plugin.

This module provides centralized debug control for the entire plugin.
Set DEBUG = True to enable debug output, False to disable.

Usage:
    from .modules.utility.debug_config import DEBUG, debug_print

    # Simple usage
    if DEBUG:
        print("Debug message")

    # Or use the helper function
    debug_print("Debug message")
"""

# Global debug flag - set to False for production
DEBUG = False

# Debug categories for fine-grained control
DEBUG_CATEGORIES = {
    'database': False,      # Database operations
    'gis': False,           # GIS/layer operations
    'ui': False,            # UI/form operations
    'ai': False,            # AI/RAG operations
    'export': False,        # Export/report operations
    'sync': False,          # Sync operations
    'all': False,           # Enable all categories
}


def debug_print(*args, category: str = None, **kwargs):
    """
    Print debug message if DEBUG is enabled.

    Args:
        *args: Arguments to print
        category: Optional category for fine-grained control
        **kwargs: Additional kwargs passed to print
    """
    if DEBUG or DEBUG_CATEGORIES.get('all', False):
        if category is None or DEBUG_CATEGORIES.get(category, False):
            print(*args, **kwargs)


def set_debug(enabled: bool):
    """Enable or disable global debug output."""
    global DEBUG
    DEBUG = enabled


def set_debug_category(category: str, enabled: bool):
    """Enable or disable a specific debug category."""
    if category in DEBUG_CATEGORIES:
        DEBUG_CATEGORIES[category] = enabled


def enable_all_debug():
    """Enable all debug output."""
    global DEBUG
    DEBUG = True
    DEBUG_CATEGORIES['all'] = True


def disable_all_debug():
    """Disable all debug output."""
    global DEBUG
    DEBUG = False
    for key in DEBUG_CATEGORIES:
        DEBUG_CATEGORIES[key] = False
