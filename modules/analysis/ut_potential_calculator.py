#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
UT Potential Calculator - Archaeological potential scoring for Unità Topografica.

Calculates archaeological potential based on weighted factors:
- Site proximity (25%): Distance from known archaeological sites
- Find density (25%): Number of finds per square meter
- Environmental factors (20%): Terrain, visibility, land use
- Chronology (15%): Dating reliability and periods
- Structure presence (15%): Nearby archaeological structures

Created for PyArchInit QGIS Plugin
"""

import json
import math
from datetime import datetime

try:
    from qgis.core import (
        QgsGeometry,
        QgsPointXY,
        QgsFeature,
        QgsVectorLayer,
        QgsProject,
        QgsDistanceArea,
        QgsCoordinateReferenceSystem,
        QgsMessageLog,
        Qgis
    )
    QGIS_AVAILABLE = True
except ImportError:
    QGIS_AVAILABLE = False


class UTPotentialCalculator:
    """
    Calculates archaeological potential score for UT records.

    The potential score ranges from 0-100 and is based on a weighted
    combination of factors that indicate the likelihood of finding
    archaeological remains in a given topographic unit.
    """

    # Default weights for each factor (must sum to 1.0)
    DEFAULT_WEIGHTS = {
        'site_proximity': 0.25,
        'find_density': 0.25,
        'environmental': 0.20,
        'chronology': 0.15,
        'structure_presence': 0.15
    }

    # Distance thresholds for site proximity (in meters)
    DISTANCE_THRESHOLDS = {
        'very_close': 100,    # < 100m = score 100
        'close': 500,         # < 500m = score 75
        'medium': 1000,       # < 1000m = score 50
        'far': 2000,          # < 2000m = score 25
        # > 2000m = score 10
    }

    # Find density thresholds (finds per m2)
    DENSITY_THRESHOLDS = {
        'very_high': 1.0,     # >= 1.0/m2 = score 100
        'high': 0.5,          # >= 0.5/m2 = score 75
        'medium': 0.1,        # >= 0.1/m2 = score 50
        'low': 0.01,          # >= 0.01/m2 = score 25
        # < 0.01/m2 = score 10
    }

    # Terrain slope categories and their scores
    SLOPE_SCORES = {
        'pianeggiante': 100,       # Flat - best for settlements
        'flat': 100,
        'lievemente ondulato': 85,
        'slightly undulating': 85,
        'ondulato': 70,
        'undulating': 70,
        'collinare': 55,
        'hilly': 55,
        'ripido': 40,
        'steep': 40,
        'molto ripido': 25,
        'very steep': 25,
        'scosceso': 10,
        'precipitous': 10,
    }

    # Land use categories and their scores
    LAND_USE_SCORES = {
        'arativo': 90,           # Arable - good visibility
        'arable': 90,
        'prato': 85,             # Meadow
        'meadow': 85,
        'pascolo': 80,           # Pasture
        'pasture': 80,
        'incolto': 75,           # Uncultivated
        'uncultivated': 75,
        'vigna': 70,             # Vineyard
        'vineyard': 70,
        'frutteto': 65,          # Orchard
        'orchard': 65,
        'oliveto': 60,           # Olive grove
        'olive grove': 60,
        'bosco': 30,             # Forest - low visibility
        'forest': 30,
        'urbano': 20,            # Urban
        'urban': 20,
        'cava': 10,              # Quarry
        'quarry': 10,
    }

    def __init__(self, db_manager=None, weights=None):
        """
        Initialize the potential calculator.

        Args:
            db_manager: PyArchInit database manager instance
            weights: Optional custom weights dictionary
        """
        self.db_manager = db_manager
        self.weights = weights or self.DEFAULT_WEIGHTS.copy()
        self._validate_weights()

    def _validate_weights(self):
        """Ensure weights sum to 1.0."""
        total = sum(self.weights.values())
        if abs(total - 1.0) > 0.001:
            # Normalize weights
            for key in self.weights:
                self.weights[key] /= total

    def log_message(self, message, level=None):
        """Log message to QGIS if available."""
        if QGIS_AVAILABLE:
            QgsMessageLog.logMessage(
                message,
                "PyArchInit UT Potential",
                level or Qgis.Info
            )

    def calculate_potential(self, ut_record, geometry=None):
        """
        Calculate the archaeological potential score for a UT record.

        Args:
            ut_record: Dictionary or object with UT data fields
            geometry: Optional QgsGeometry for spatial calculations

        Returns:
            Dictionary containing:
                - total_score: Overall potential score (0-100)
                - factor_scores: Individual factor scores
                - factor_contributions: Weighted contributions
                - interpretation: Text interpretation of score
                - analysis_date: Timestamp of analysis
        """
        try:
            # Convert record to dict if needed
            if hasattr(ut_record, '__dict__'):
                data = {k: v for k, v in ut_record.__dict__.items()
                       if not k.startswith('_')}
            else:
                data = dict(ut_record) if ut_record else {}

            # Calculate individual factor scores
            factor_scores = {
                'site_proximity': self._calculate_site_proximity(data, geometry),
                'find_density': self._calculate_find_density(data),
                'environmental': self._calculate_environmental(data),
                'chronology': self._calculate_chronology(data),
                'structure_presence': self._calculate_structure_presence(data, geometry)
            }

            # Calculate weighted contributions
            factor_contributions = {}
            for factor, score in factor_scores.items():
                weight = self.weights.get(factor, 0)
                factor_contributions[factor] = {
                    'score': score,
                    'weight': weight,
                    'contribution': score * weight
                }

            # Calculate total score
            total_score = sum(fc['contribution'] for fc in factor_contributions.values())
            total_score = round(min(100, max(0, total_score)), 2)

            # Generate interpretation
            interpretation = self._generate_interpretation(total_score, factor_scores)

            return {
                'total_score': total_score,
                'factor_scores': factor_scores,
                'factor_contributions': factor_contributions,
                'interpretation': interpretation,
                'analysis_date': datetime.now().isoformat(),
                'method': 'weighted_scoring'
            }

        except Exception as e:
            self.log_message(f"Error calculating potential: {e}", Qgis.Warning if QGIS_AVAILABLE else None)
            return {
                'total_score': 0,
                'factor_scores': {},
                'factor_contributions': {},
                'interpretation': f'Error: {str(e)}',
                'analysis_date': datetime.now().isoformat(),
                'method': 'error'
            }

    def _calculate_site_proximity(self, data, geometry=None):
        """
        Calculate score based on proximity to known archaeological sites.

        Args:
            data: UT record data
            geometry: UT geometry for distance calculations

        Returns:
            Score 0-100 based on distance to nearest site
        """
        if not self.db_manager or not geometry:
            # Use stored proximity data if available
            proximity = data.get('proximity_to_sites')
            if proximity is not None:
                try:
                    return float(proximity)
                except (ValueError, TypeError):
                    pass
            return 50  # Default medium score if no data

        try:
            # Query nearby sites from database
            from sqlalchemy import text

            # Get centroid of UT geometry
            if QGIS_AVAILABLE and geometry:
                centroid = geometry.centroid().asPoint()
                x, y = centroid.x(), centroid.y()
            else:
                return 50

            # Query site_table for nearby sites
            # This is a simplified approach - real implementation should use spatial queries
            sites = self.db_manager.query_bool({}, 'SITE')

            if not sites:
                return 10  # No sites = low score

            # Calculate distances to all sites
            # In production, use PostGIS ST_Distance or SpatiaLite distance
            min_distance = float('inf')

            for site in sites:
                # Get site location if available
                site_x = getattr(site, 'coord_x', None) or getattr(site, 'est', None)
                site_y = getattr(site, 'coord_y', None) or getattr(site, 'nord', None)

                if site_x and site_y:
                    try:
                        dist = math.sqrt((x - float(site_x))**2 + (y - float(site_y))**2)
                        min_distance = min(min_distance, dist)
                    except (ValueError, TypeError):
                        continue

            # Convert distance to score
            if min_distance < self.DISTANCE_THRESHOLDS['very_close']:
                return 100
            elif min_distance < self.DISTANCE_THRESHOLDS['close']:
                return 75
            elif min_distance < self.DISTANCE_THRESHOLDS['medium']:
                return 50
            elif min_distance < self.DISTANCE_THRESHOLDS['far']:
                return 25
            else:
                return 10

        except Exception as e:
            self.log_message(f"Site proximity calculation error: {e}")
            return 50

    def _calculate_find_density(self, data):
        """
        Calculate score based on find density (rep_per_mq).

        Args:
            data: UT record data

        Returns:
            Score 0-100 based on find density
        """
        # Try to get rep_per_mq from data
        density = data.get('rep_per_mq')

        if density is None:
            # Try to calculate from related finds if db_manager available
            if self.db_manager:
                try:
                    sito = data.get('progetto') or data.get('sito')
                    nr_ut = data.get('nr_ut')

                    if sito and nr_ut:
                        # Count related finds from inventario_materiali_table
                        finds = self.db_manager.query_bool(
                            {'sito': sito, 'nr_ut': str(nr_ut)},
                            'INVENTARIO_MATERIALI'
                        )

                        if finds:
                            # Get area if available
                            area = data.get('superficie') or data.get('area_mq') or 1
                            try:
                                area = float(area)
                                if area > 0:
                                    density = len(finds) / area
                            except (ValueError, TypeError):
                                density = len(finds) / 100  # Assume 100 m2 default
                except Exception as e:
                    self.log_message(f"Find density calculation error: {e}")

        if density is None:
            return 50  # Default medium score

        try:
            density = float(density)
        except (ValueError, TypeError):
            return 50

        # Convert density to score
        if density >= self.DENSITY_THRESHOLDS['very_high']:
            return 100
        elif density >= self.DENSITY_THRESHOLDS['high']:
            return 75
        elif density >= self.DENSITY_THRESHOLDS['medium']:
            return 50
        elif density >= self.DENSITY_THRESHOLDS['low']:
            return 25
        else:
            return 10

    def _calculate_environmental(self, data):
        """
        Calculate score based on environmental factors.

        Args:
            data: UT record data

        Returns:
            Score 0-100 based on terrain, visibility, and land use
        """
        scores = []

        # Terrain slope
        slope = data.get('andamento_terreno_pendenza', '').lower()
        if slope:
            slope_score = self.SLOPE_SCORES.get(slope)
            if slope_score is None:
                # Partial match
                for key, value in self.SLOPE_SCORES.items():
                    if key in slope or slope in key:
                        slope_score = value
                        break
            if slope_score:
                scores.append(slope_score)

        # Visibility percentage
        visibility = data.get('visibility_percent')
        if visibility is not None:
            try:
                vis_score = float(visibility)
                scores.append(min(100, max(0, vis_score)))
            except (ValueError, TypeError):
                pass

        # Land use
        land_use = data.get('utilizzo_suolo_vegetazione', '').lower()
        if land_use:
            land_score = self.LAND_USE_SCORES.get(land_use)
            if land_score is None:
                # Partial match
                for key, value in self.LAND_USE_SCORES.items():
                    if key in land_use or land_use in key:
                        land_score = value
                        break
            if land_score:
                scores.append(land_score)

        if scores:
            return sum(scores) / len(scores)
        return 50  # Default

    def _calculate_chronology(self, data):
        """
        Calculate score based on chronological/dating information.

        Args:
            data: UT record data

        Returns:
            Score 0-100 based on dating reliability and periods
        """
        scores = []

        # Check for period assignments
        periodo = data.get('periodo_iniziale') or data.get('periodo')
        fase = data.get('fase_iniziale') or data.get('fase')
        datazione = data.get('datazione_estesa')

        # More specific dating = higher score
        if periodo and fase:
            scores.append(100)  # Both period and phase defined
        elif periodo:
            scores.append(75)   # Only period
        elif datazione:
            scores.append(60)   # General dating

        # Check for period range (broader range = lower certainty)
        periodo_finale = data.get('periodo_finale')
        if periodo and periodo_finale:
            if periodo == periodo_finale:
                scores.append(90)  # Same period = certain
            else:
                scores.append(60)  # Range = less certain

        # Check for archaeological materials indicator
        if data.get('materiali_segnalati') or data.get('campioni'):
            scores.append(80)

        if scores:
            return sum(scores) / len(scores)
        return 40  # Lower default for unknown chronology

    def _calculate_structure_presence(self, data, geometry=None):
        """
        Calculate score based on presence of nearby archaeological structures.

        Args:
            data: UT record data
            geometry: UT geometry for spatial queries

        Returns:
            Score 0-100 based on structure presence
        """
        if not self.db_manager:
            # Check if structure-related fields have values
            has_structures = (
                data.get('struttura') or
                data.get('nr_struttura') or
                data.get('strutture_associate')
            )
            return 80 if has_structures else 40

        try:
            sito = data.get('progetto') or data.get('sito')

            if sito:
                # Query struttura_table for related structures
                structures = self.db_manager.query_bool(
                    {'sito': sito},
                    'STRUTTURA'
                )

                if structures:
                    # More structures = higher score
                    count = len(structures)
                    if count >= 10:
                        return 100
                    elif count >= 5:
                        return 85
                    elif count >= 2:
                        return 70
                    else:
                        return 55
                else:
                    return 30  # No structures in site

            return 40

        except Exception as e:
            self.log_message(f"Structure presence calculation error: {e}")
            return 40

    def _generate_interpretation(self, total_score, factor_scores):
        """
        Generate a text interpretation of the potential score.

        Args:
            total_score: Overall potential score
            factor_scores: Individual factor scores

        Returns:
            Text interpretation string
        """
        # Determine level
        if total_score >= 80:
            level = "molto alto"
            level_desc = "L'area presenta caratteristiche fortemente indicative di presenza archeologica."
        elif total_score >= 60:
            level = "alto"
            level_desc = "L'area mostra numerosi indicatori di potenziale archeologico."
        elif total_score >= 40:
            level = "medio"
            level_desc = "L'area presenta alcuni indicatori di potenziale archeologico."
        elif total_score >= 20:
            level = "basso"
            level_desc = "L'area mostra pochi indicatori di potenziale archeologico."
        else:
            level = "molto basso"
            level_desc = "L'area non presenta significativi indicatori di potenziale archeologico."

        # Find strongest and weakest factors
        if factor_scores:
            strongest = max(factor_scores.items(), key=lambda x: x[1])
            weakest = min(factor_scores.items(), key=lambda x: x[1])

            factor_names = {
                'site_proximity': 'prossimità a siti noti',
                'find_density': 'densità dei reperti',
                'environmental': 'fattori ambientali',
                'chronology': 'dati cronologici',
                'structure_presence': 'presenza di strutture'
            }

            return (
                f"Potenziale archeologico {level} (punteggio: {total_score:.1f}/100). "
                f"{level_desc} "
                f"Il fattore più favorevole è la {factor_names.get(strongest[0], strongest[0])} "
                f"({strongest[1]:.0f}/100), mentre il più debole è la "
                f"{factor_names.get(weakest[0], weakest[0])} ({weakest[1]:.0f}/100)."
            )

        return f"Potenziale archeologico {level} (punteggio: {total_score:.1f}/100). {level_desc}"

    def to_json(self, result):
        """
        Convert calculation result to JSON string.

        Args:
            result: Dictionary from calculate_potential()

        Returns:
            JSON string
        """
        return json.dumps(result, ensure_ascii=False, indent=2)

    @staticmethod
    def from_json(json_str):
        """
        Parse JSON string to result dictionary.

        Args:
            json_str: JSON string

        Returns:
            Dictionary
        """
        return json.loads(json_str) if json_str else {}
