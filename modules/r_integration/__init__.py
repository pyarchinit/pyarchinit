# -*- coding: utf-8 -*-
"""
R Integration Module for PyArchInit

This module provides R integration for geostatistical analysis in the
Archeozoology module using PyPER (Python-R bridge).

Components:
- RSessionManager: Manages R session lifecycle
- ArcheozooRAnalysis: Provides R-based analysis functions
"""

from .r_session_manager import RSessionManager

__all__ = ['RSessionManager']
