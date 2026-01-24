#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
UT Risk Assessor - Archaeological risk assessment for Unità Topografica.

Calculates archaeological risk based on weighted factors:
- Urban development (30%): Proximity to urbanized areas and construction
- Natural erosion (20%): Risk from slope, drainage, weathering
- Agricultural activity (20%): Intensity of agricultural works
- Conservation state (15%): Current condition of deposits
- Discovery probability (15%): Probability of finding remains

Created for PyArchInit QGIS Plugin
"""

import json
import math
from datetime import datetime

try:
    from qgis.core import (
        QgsGeometry,
        QgsPointXY,
        QgsMessageLog,
        Qgis
    )
    QGIS_AVAILABLE = True
except ImportError:
    QGIS_AVAILABLE = False


class UTRiskAssessor:
    """
    Calculates archaeological risk score for UT records.

    The risk score ranges from 0-100 and indicates the level of threat
    to archaeological heritage from various sources including development,
    erosion, and agricultural activities.
    """

    # Default weights for each factor (must sum to 1.0)
    DEFAULT_WEIGHTS = {
        'urban_development': 0.30,
        'natural_erosion': 0.20,
        'agricultural_activity': 0.20,
        'conservation_state': 0.15,
        'discovery_probability': 0.15
    }

    # Terrain slope risk scores (steeper = more erosion risk)
    SLOPE_RISK_SCORES = {
        'pianeggiante': 20,        # Flat - low erosion risk
        'flat': 20,
        'lievemente ondulato': 35,
        'slightly undulating': 35,
        'ondulato': 50,
        'undulating': 50,
        'collinare': 65,
        'hilly': 65,
        'ripido': 80,
        'steep': 80,
        'molto ripido': 90,
        'very steep': 90,
        'scosceso': 100,
        'precipitous': 100,
    }

    # Land use risk scores (more intensive = more risk)
    LAND_USE_RISK = {
        'arativo': 85,           # Arable - high plowing risk
        'arable': 85,
        'vigna': 90,             # Vineyard - deep roots
        'vineyard': 90,
        'frutteto': 80,          # Orchard
        'orchard': 80,
        'oliveto': 75,           # Olive grove
        'olive grove': 75,
        'cava': 100,             # Quarry - destruction
        'quarry': 100,
        'urbano': 95,            # Urban - construction
        'urban': 95,
        'pascolo': 40,           # Pasture - low risk
        'pasture': 40,
        'prato': 30,             # Meadow
        'meadow': 30,
        'bosco': 35,             # Forest - root damage
        'forest': 35,
        'incolto': 25,           # Uncultivated
        'uncultivated': 25,
    }

    # Conservation state mapping
    CONSERVATION_RISK = {
        'ottimo': 10,            # Excellent = low risk
        'excellent': 10,
        'buono': 25,             # Good
        'good': 25,
        'discreto': 45,          # Fair
        'fair': 45,
        'mediocre': 60,          # Mediocre
        'poor': 60,
        'cattivo': 80,           # Bad
        'bad': 80,
        'pessimo': 95,           # Very bad
        'very bad': 95,
        'distrutto': 100,        # Destroyed
        'destroyed': 100,
    }

    def __init__(self, db_manager=None, weights=None, potential_calculator=None):
        """
        Initialize the risk assessor.

        Args:
            db_manager: PyArchInit database manager instance
            weights: Optional custom weights dictionary
            potential_calculator: Optional UTPotentialCalculator for discovery probability
        """
        self.db_manager = db_manager
        self.weights = weights or self.DEFAULT_WEIGHTS.copy()
        self.potential_calculator = potential_calculator
        self._validate_weights()

    def _validate_weights(self):
        """Ensure weights sum to 1.0."""
        total = sum(self.weights.values())
        if abs(total - 1.0) > 0.001:
            for key in self.weights:
                self.weights[key] /= total

    def log_message(self, message, level=None):
        """Log message to QGIS if available."""
        if QGIS_AVAILABLE:
            QgsMessageLog.logMessage(
                message,
                "PyArchInit UT Risk",
                level or Qgis.Info
            )

    def calculate_risk(self, ut_record, geometry=None, potential_score=None):
        """
        Calculate the archaeological risk score for a UT record.

        Args:
            ut_record: Dictionary or object with UT data fields
            geometry: Optional QgsGeometry for spatial calculations
            potential_score: Optional pre-calculated potential score (0-100)

        Returns:
            Dictionary containing:
                - total_score: Overall risk score (0-100)
                - factor_scores: Individual factor scores
                - factor_contributions: Weighted contributions
                - interpretation: Text interpretation
                - recommendations: Risk mitigation recommendations
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
                'urban_development': self._calculate_urban_development(data, geometry),
                'natural_erosion': self._calculate_natural_erosion(data),
                'agricultural_activity': self._calculate_agricultural_activity(data),
                'conservation_state': self._calculate_conservation_state(data),
                'discovery_probability': self._calculate_discovery_probability(data, geometry, potential_score)
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

            # Generate interpretation and recommendations
            interpretation = self._generate_interpretation(total_score, factor_scores)
            recommendations = self._generate_recommendations(total_score, factor_scores)

            return {
                'total_score': total_score,
                'factor_scores': factor_scores,
                'factor_contributions': factor_contributions,
                'interpretation': interpretation,
                'recommendations': recommendations,
                'analysis_date': datetime.now().isoformat(),
                'method': 'weighted_risk_assessment'
            }

        except Exception as e:
            self.log_message(f"Error calculating risk: {e}", Qgis.Warning if QGIS_AVAILABLE else None)
            return {
                'total_score': 0,
                'factor_scores': {},
                'factor_contributions': {},
                'interpretation': f'Error: {str(e)}',
                'recommendations': [],
                'analysis_date': datetime.now().isoformat(),
                'method': 'error'
            }

    def _calculate_urban_development(self, data, geometry=None):
        """
        Calculate risk from urban development and construction.

        Args:
            data: UT record data
            geometry: UT geometry for proximity calculations

        Returns:
            Score 0-100 (higher = more risk)
        """
        scores = []

        # Check land use for urban indicators
        land_use = data.get('utilizzo_suolo_vegetazione', '').lower()
        if 'urban' in land_use or 'urbano' in land_use:
            scores.append(95)
        elif 'industriale' in land_use or 'industrial' in land_use:
            scores.append(90)
        elif 'commerciale' in land_use or 'commercial' in land_use:
            scores.append(85)
        elif 'residenziale' in land_use or 'residential' in land_use:
            scores.append(80)

        # Check for building activity indicators
        attivita = data.get('attivita', '').lower()
        if 'costruzione' in attivita or 'construction' in attivita:
            scores.append(100)
        elif 'scavo' in attivita or 'excavation' in attivita:
            scores.append(80)

        # Check comune/location for urban proximity
        comune = data.get('comune', '').lower()
        provincia = data.get('provincia', '').lower()

        # Large cities = higher development risk
        major_cities = ['roma', 'milano', 'napoli', 'torino', 'firenze', 'palermo',
                       'bologna', 'genova', 'bari', 'catania', 'venezia']
        for city in major_cities:
            if city in comune or city in provincia:
                scores.append(70)
                break

        # If no specific indicators, use moderate default
        if scores:
            return sum(scores) / len(scores)
        return 40  # Default moderate risk

    def _calculate_natural_erosion(self, data):
        """
        Calculate risk from natural erosion factors.

        Args:
            data: UT record data

        Returns:
            Score 0-100 (higher = more risk)
        """
        scores = []

        # Terrain slope - steeper = more erosion
        slope = data.get('andamento_terreno_pendenza', '').lower()
        if slope:
            slope_risk = self.SLOPE_RISK_SCORES.get(slope)
            if slope_risk is None:
                for key, value in self.SLOPE_RISK_SCORES.items():
                    if key in slope or slope in key:
                        slope_risk = value
                        break
            if slope_risk:
                scores.append(slope_risk)

        # Drainage/water risk
        idrografia = data.get('idrografia', '').lower()
        if 'fiume' in idrografia or 'river' in idrografia:
            scores.append(75)  # Near river = flood risk
        elif 'torrente' in idrografia or 'stream' in idrografia:
            scores.append(65)
        elif 'lago' in idrografia or 'lake' in idrografia:
            scores.append(55)
        elif 'mare' in idrografia or 'sea' in idrografia:
            scores.append(70)  # Coastal erosion

        # Geology - some types more prone to erosion
        geologia = data.get('geologia', '').lower()
        if 'argilla' in geologia or 'clay' in geologia:
            scores.append(60)  # Erosion prone
        elif 'sabbia' in geologia or 'sand' in geologia:
            scores.append(70)
        elif 'ghiaia' in geologia or 'gravel' in geologia:
            scores.append(55)
        elif 'roccia' in geologia or 'rock' in geologia:
            scores.append(25)  # Stable

        if scores:
            return sum(scores) / len(scores)
        return 40  # Default

    def _calculate_agricultural_activity(self, data):
        """
        Calculate risk from agricultural activities.

        Args:
            data: UT record data

        Returns:
            Score 0-100 (higher = more risk)
        """
        scores = []

        # Land use - agriculture type
        land_use = data.get('utilizzo_suolo_vegetazione', '').lower()
        if land_use:
            ag_risk = self.LAND_USE_RISK.get(land_use)
            if ag_risk is None:
                for key, value in self.LAND_USE_RISK.items():
                    if key in land_use or land_use in key:
                        ag_risk = value
                        break
            if ag_risk:
                scores.append(ag_risk)

        # Check for specific agricultural indicators
        coltivazione = data.get('coltivazione', '').lower()
        if 'aratura profonda' in coltivazione or 'deep plowing' in coltivazione:
            scores.append(95)
        elif 'aratura' in coltivazione or 'plowing' in coltivazione:
            scores.append(80)
        elif 'fresatura' in coltivazione or 'tilling' in coltivazione:
            scores.append(70)

        # Vegetation type impact
        vegetazione = data.get('vegetazione', '').lower()
        if 'cereali' in vegetazione or 'cereals' in vegetazione:
            scores.append(75)  # Annual plowing
        elif 'vite' in vegetazione or 'vine' in vegetazione:
            scores.append(85)  # Deep roots
        elif 'olivo' in vegetazione or 'olive' in vegetazione:
            scores.append(70)

        if scores:
            return sum(scores) / len(scores)
        return 45  # Default moderate

    def _calculate_conservation_state(self, data):
        """
        Calculate risk based on current conservation state.

        Note: Poor conservation = higher immediate risk to remaining deposits.

        Args:
            data: UT record data

        Returns:
            Score 0-100 (higher = more risk)
        """
        # Check stato_conservazione or similar fields
        stato = data.get('stato_conservazione', '').lower()

        if stato:
            risk = self.CONSERVATION_RISK.get(stato)
            if risk is None:
                for key, value in self.CONSERVATION_RISK.items():
                    if key in stato or stato in key:
                        risk = value
                        break
            if risk:
                return risk

        # Check for damage indicators
        danni = data.get('danni', '').lower()
        if 'grave' in danni or 'severe' in danni:
            return 85
        elif 'moderato' in danni or 'moderate' in danni:
            return 60
        elif 'lieve' in danni or 'slight' in danni:
            return 35

        return 50  # Default unknown state

    def _calculate_discovery_probability(self, data, geometry=None, potential_score=None):
        """
        Calculate risk based on probability of finding remains.

        Higher discovery probability = higher risk if not protected.

        Args:
            data: UT record data
            geometry: UT geometry
            potential_score: Optional pre-calculated potential score

        Returns:
            Score 0-100 (higher potential = higher risk)
        """
        # Use provided potential score if available
        if potential_score is not None:
            try:
                return float(potential_score)
            except (ValueError, TypeError):
                pass

        # Try to calculate potential score using calculator
        if self.potential_calculator:
            try:
                result = self.potential_calculator.calculate_potential(data, geometry)
                return result.get('total_score', 50)
            except Exception:
                pass

        # Fallback: estimate from available data
        indicators = 0
        max_indicators = 5

        # Check for finds
        if data.get('rep_per_mq') or data.get('reperti_segnalati'):
            indicators += 1

        # Check for dating
        if data.get('periodo_iniziale') or data.get('datazione_estesa'):
            indicators += 1

        # Check for structures
        if data.get('struttura') or data.get('nr_struttura'):
            indicators += 1

        # Check for positive interpretation
        interp = data.get('interpretazione_ut', '').lower()
        if 'archeologico' in interp or 'sito' in interp or 'insediamento' in interp:
            indicators += 1

        # Check for samples
        if data.get('campioni') or data.get('materiali_segnalati'):
            indicators += 1

        # Convert to 0-100 scale
        return (indicators / max_indicators) * 100

    def _generate_interpretation(self, total_score, factor_scores):
        """
        Generate a text interpretation of the risk score.

        Args:
            total_score: Overall risk score
            factor_scores: Individual factor scores

        Returns:
            Text interpretation string
        """
        if total_score >= 80:
            level = "molto alto"
            level_desc = "L'area è soggetta a gravi minacce che richiedono interventi urgenti."
        elif total_score >= 60:
            level = "alto"
            level_desc = "L'area presenta significative minacce al patrimonio archeologico."
        elif total_score >= 40:
            level = "medio"
            level_desc = "L'area presenta alcune minacce che richiedono monitoraggio."
        elif total_score >= 20:
            level = "basso"
            level_desc = "L'area presenta minacce limitate al patrimonio archeologico."
        else:
            level = "molto basso"
            level_desc = "L'area presenta minime minacce al patrimonio archeologico."

        # Find main risk factors
        if factor_scores:
            highest = max(factor_scores.items(), key=lambda x: x[1])

            factor_names = {
                'urban_development': 'sviluppo urbanistico',
                'natural_erosion': 'erosione naturale',
                'agricultural_activity': 'attività agricola',
                'conservation_state': 'stato di conservazione',
                'discovery_probability': 'probabilità di scoperta'
            }

            return (
                f"Rischio archeologico {level} (punteggio: {total_score:.1f}/100). "
                f"{level_desc} "
                f"Il principale fattore di rischio è {factor_names.get(highest[0], highest[0])} "
                f"({highest[1]:.0f}/100)."
            )

        return f"Rischio archeologico {level} (punteggio: {total_score:.1f}/100). {level_desc}"

    def _generate_recommendations(self, total_score, factor_scores):
        """
        Generate risk mitigation recommendations.

        Args:
            total_score: Overall risk score
            factor_scores: Individual factor scores

        Returns:
            List of recommendation strings
        """
        recommendations = []

        # General recommendations based on total score
        if total_score >= 80:
            recommendations.append("PRIORITA' ALTA: Avviare immediatamente misure di protezione e monitoraggio.")
        elif total_score >= 60:
            recommendations.append("Implementare un programma di monitoraggio regolare dell'area.")

        # Specific recommendations based on factor scores
        if factor_scores.get('urban_development', 0) >= 70:
            recommendations.append(
                "Richiedere valutazione di impatto archeologico per qualsiasi intervento edilizio."
            )

        if factor_scores.get('natural_erosion', 0) >= 70:
            recommendations.append(
                "Valutare interventi di consolidamento e protezione contro l'erosione."
            )

        if factor_scores.get('agricultural_activity', 0) >= 70:
            recommendations.append(
                "Limitare le lavorazioni agricole profonde e considerare conversione a prato."
            )

        if factor_scores.get('conservation_state', 0) >= 70:
            recommendations.append(
                "Avviare urgentemente interventi di conservazione e restauro."
            )

        if factor_scores.get('discovery_probability', 0) >= 70:
            recommendations.append(
                "Considerare indagini archeologiche preventive prima di qualsiasi intervento."
            )

        # Add documentation recommendation if no other recommendations
        if not recommendations:
            recommendations.append(
                "Mantenere documentazione aggiornata e monitoraggio periodico dell'area."
            )

        return recommendations

    def to_json(self, result):
        """
        Convert assessment result to JSON string.

        Args:
            result: Dictionary from calculate_risk()

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
