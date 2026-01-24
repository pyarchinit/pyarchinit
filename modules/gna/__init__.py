# -*- coding: utf-8 -*-
"""
PyArchInit GNA Integration Module

This module provides integration with the Italian GNA (Geoportale Nazionale
per l'Archeologia) template for archaeological data export.

Features:
- Export UT data to GNA GeoPackage format
- Map PyArchInit thesaurus to GNA controlled vocabularies
- Generate VRP (Archaeological Potential) and VRD (Archaeological Risk) layers
- Polygon-masked heatmap generation for irregular project areas

GNA Template Version: 1.5
"""

from .gna_vocabulary_mapper import GNAVocabularyMapper
from .gna_field_mapper import GNAFieldMapper
from .gna_layer_builder import GNALayerBuilder
from .gna_exporter import GNAExporter
from .gna_labels import GNA_LABELS

__all__ = [
    'GNAVocabularyMapper',
    'GNAFieldMapper',
    'GNALayerBuilder',
    'GNAExporter',
    'GNA_LABELS',
]

__version__ = '1.0.0'
