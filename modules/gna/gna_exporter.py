# -*- coding: utf-8 -*-
"""
GNA Exporter

Main export class for PyArchInit UT data to GNA GeoPackage format.

Creates a GeoPackage with:
- MOPR: Project perimeter layer
- MOSI_point: Point-based UT records
- MOSI_polygon: Polygon-based UT records (if available)
- VRP: Archaeological potential classification map
- VRD: Archaeological risk classification map

GNA Template: Geoportale Nazionale per l'Archeologia v1.5
"""

import os
from datetime import datetime

from qgis.core import (
    QgsVectorLayer,
    QgsVectorFileWriter,
    QgsCoordinateReferenceSystem,
    QgsCoordinateTransformContext,
    QgsProject,
    QgsMessageLog,
    Qgis
)

from .gna_vocabulary_mapper import GNAVocabularyMapper
from .gna_field_mapper import GNAFieldMapper
from .gna_layer_builder import GNALayerBuilder


class GNAExporter:
    """
    Exports PyArchInit UT data to GNA-compliant GeoPackage.

    Usage:
        exporter = GNAExporter(db_manager, 'ProjectName', '/path/output.gpkg')
        result = exporter.export(project_polygon, ut_records, options)
    """

    # Default CRS for GNA export (WGS84 recommended)
    DEFAULT_CRS = 'EPSG:4326'

    def __init__(self, db_manager, project_name, output_path,
                 crs=None, language='it'):
        """
        Initialize GNA exporter.

        Args:
            db_manager: PyArchInit database manager
            project_name: Name of the project (used for CPR code)
            output_path: Path for output GeoPackage file
            crs: QgsCoordinateReferenceSystem (default WGS84)
            language: Language code for translations
        """
        self.db_manager = db_manager
        self.project_name = project_name
        self.output_path = output_path
        self.crs = crs or QgsCoordinateReferenceSystem(self.DEFAULT_CRS)
        self.language = language

        # Initialize mappers and builders
        self.vocab_mapper = GNAVocabularyMapper(language)
        self.field_mapper = GNAFieldMapper(language)
        self.layer_builder = GNALayerBuilder(self.crs, language)

        # Track created layers for reporting
        self.created_layers = []
        self.errors = []
        self.warnings = []

    def export(self, project_polygon, ut_records, options=None):
        """
        Export UT data to GNA GeoPackage.

        Args:
            project_polygon: QgsGeometry of project area (MOPR)
            ut_records: List of UT database records to export
            options: Dict with export options:
                - generate_mosi: bool (default True)
                - generate_vrp: bool (default True)
                - generate_vrd: bool (default True)
                - heatmap_method: 'kde', 'idw', or 'grid' (default 'kde')
                - cell_size: int (default 50)
                - project_info: dict with title, responsible, dates, etc.
                - geometries: dict mapping record IDs to QgsGeometry

        Returns:
            Dict with:
                - success: bool
                - gpkg_path: output file path
                - layers: list of created layer names
                - record_count: number of records exported
                - errors: list of error messages
                - warnings: list of warning messages
        """
        options = options or {}
        self.errors = []
        self.warnings = []
        self.created_layers = []

        # Validate inputs
        validation = self._validate_inputs(project_polygon, ut_records)
        if not validation['valid']:
            return {
                'success': False,
                'errors': validation['errors'],
                'gpkg_path': None,
                'layers': [],
                'record_count': 0,
            }

        try:
            # Ensure output directory exists
            output_dir = os.path.dirname(self.output_path)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)

            # 1. Create MOPR layer
            self._log("Creating MOPR layer...")
            mopr_layer = self._create_mopr_layer(
                project_polygon,
                options.get('project_info', {})
            )
            if mopr_layer:
                self._save_layer_to_gpkg(mopr_layer, 'MOPR', create_new=True)
                self.created_layers.append('MOPR')

            # 2. Create MOSI layers
            if options.get('generate_mosi', True):
                self._log("Creating MOSI layers...")
                mosi_result = self._create_mosi_layers(
                    ut_records,
                    options.get('geometries', {})
                )
                if mosi_result.get('point_layer'):
                    self._save_layer_to_gpkg(mosi_result['point_layer'], 'MOSI_point')
                    self.created_layers.append('MOSI_point')
                if mosi_result.get('polygon_layer'):
                    self._save_layer_to_gpkg(mosi_result['polygon_layer'], 'MOSI_polygon')
                    self.created_layers.append('MOSI_polygon')

            # 3. Generate VRP layer
            if options.get('generate_vrp', True):
                self._log("Generating VRP layer...")
                vrp_layer = self._create_vrp_layer(
                    ut_records,
                    project_polygon,
                    options
                )
                if vrp_layer:
                    self._save_layer_to_gpkg(vrp_layer, 'VRP')
                    self.created_layers.append('VRP')

            # 4. Generate VRD layer
            if options.get('generate_vrd', True):
                self._log("Generating VRD layer...")
                vrd_layer = self._create_vrd_layer(
                    ut_records,
                    project_polygon,
                    options
                )
                if vrd_layer:
                    self._save_layer_to_gpkg(vrd_layer, 'VRD')
                    self.created_layers.append('VRD')

            return {
                'success': True,
                'gpkg_path': self.output_path,
                'layers': self.created_layers,
                'record_count': len(ut_records),
                'errors': self.errors,
                'warnings': self.warnings,
                'timestamp': datetime.now().isoformat(),
            }

        except Exception as e:
            self._log(f"Export error: {e}", Qgis.Critical)
            return {
                'success': False,
                'gpkg_path': None,
                'layers': self.created_layers,
                'record_count': 0,
                'errors': self.errors + [str(e)],
                'warnings': self.warnings,
            }

    def _validate_inputs(self, project_polygon, ut_records):
        """Validate export inputs."""
        errors = []

        if not project_polygon or project_polygon.isEmpty():
            errors.append("Invalid or empty project polygon")

        if not project_polygon.isGeosValid():
            # Try to fix invalid geometry
            fixed = project_polygon.makeValid()
            if fixed.isGeosValid():
                self.warnings.append("Project polygon was automatically fixed")
            else:
                errors.append("Invalid project polygon geometry that cannot be fixed")

        if not ut_records:
            errors.append("No UT records to export")

        # Check that output path has .gpkg extension
        if not self.output_path.lower().endswith('.gpkg'):
            self.output_path += '.gpkg'

        return {
            'valid': len(errors) == 0,
            'errors': errors,
        }

    def _create_mopr_layer(self, polygon, project_info):
        """Create MOPR layer with project info."""
        # Build project info with defaults
        info = {
            'code': self._generate_project_code(),
            'title': project_info.get('title', self.project_name),
            'responsible': project_info.get('responsible', ''),
            'start_date': project_info.get('start_date'),
            'end_date': project_info.get('end_date'),
            'notes': project_info.get('notes', ''),
        }

        return self.layer_builder.build_mopr_layer(polygon, info)

    def _create_mosi_layers(self, ut_records, geometries):
        """Create MOSI point and polygon layers."""
        return self.layer_builder.build_mosi_layers(ut_records, geometries)

    def _create_vrp_layer(self, ut_records, project_polygon, options):
        """Create VRP (potential) layer using heatmap generation."""
        # Extract potential scores and coordinates
        points, values = self._extract_scores_and_coordinates(
            ut_records, 'potential_score', options.get('geometries', {})
        )

        if not points or not values:
            self.warnings.append("No potential scores available for VRP generation")
            return None

        # Get classification scheme
        vrp_scheme = self.vocab_mapper.get_vrp_classification_scheme()

        # Generate masked heatmap
        return self._generate_classified_heatmap(
            points, values, project_polygon,
            vrp_scheme, 'VRP', options
        )

    def _create_vrd_layer(self, ut_records, project_polygon, options):
        """Create VRD (risk) layer using heatmap generation."""
        # Extract risk scores and coordinates
        points, values = self._extract_scores_and_coordinates(
            ut_records, 'risk_score', options.get('geometries', {})
        )

        if not points or not values:
            self.warnings.append("No risk scores available for VRD generation")
            return None

        # Get classification scheme
        vrd_scheme = self.vocab_mapper.get_vrd_classification_scheme()

        # Generate masked heatmap
        return self._generate_classified_heatmap(
            points, values, project_polygon,
            vrd_scheme, 'VRD', options
        )

    def _extract_scores_and_coordinates(self, ut_records, score_field, geometries):
        """
        Extract coordinate points and score values from UT records.

        Args:
            ut_records: List of UT records
            score_field: Name of score attribute ('potential_score' or 'risk_score')
            geometries: Dict mapping record IDs to geometries

        Returns:
            Tuple of (points list, values list)
        """
        points = []
        values = []

        for record in ut_records:
            # Get score
            score = getattr(record, score_field, None)
            if score is None:
                continue

            try:
                score = float(score)
            except (ValueError, TypeError):
                continue

            # Get coordinates
            record_id = getattr(record, 'id_ut', None) or getattr(record, 'nr_ut', None)
            geom = geometries.get(record_id)

            if geom:
                # Use geometry centroid
                centroid = geom.centroid().asPoint()
                x, y = centroid.x(), centroid.y()
            else:
                # Try to extract from record fields
                coords = self._get_coordinates_from_record(record)
                if not coords:
                    continue
                x, y = coords

            points.append((x, y))
            values.append(score)

        return points, values

    def _get_coordinates_from_record(self, record):
        """Extract coordinates from UT record fields."""
        # Try coord_piane
        coord_piane = getattr(record, 'coord_piane', None)
        if coord_piane:
            try:
                parts = str(coord_piane).replace(';', ',').split(',')
                if len(parts) >= 2:
                    return float(parts[0].strip()), float(parts[1].strip())
            except:
                pass

        # Try coord_geografiche
        coord_geo = getattr(record, 'coord_geografiche', None)
        if coord_geo:
            try:
                parts = str(coord_geo).replace(';', ',').split(',')
                if len(parts) >= 2:
                    # Assuming lat, lon - return as lon, lat for x, y
                    lat = float(parts[0].strip())
                    lon = float(parts[1].strip())
                    return lon, lat
            except:
                pass

        return None

    def _generate_classified_heatmap(self, points, values, mask_polygon,
                                      classification_scheme, layer_name, options):
        """
        Generate a classified heatmap layer.

        Args:
            points: List of (x, y) coordinates
            values: List of score values
            mask_polygon: QgsGeometry of project boundary
            classification_scheme: Dict for classification
            layer_name: Name for output layer
            options: Export options

        Returns:
            QgsVectorLayer or None
        """
        try:
            from ..analysis.ut_heatmap_generator import UTHeatmapGenerator

            # Create heatmap generator
            generator = UTHeatmapGenerator(
                output_dir=os.path.dirname(self.output_path),
                crs=self.crs
            )

            # Generate masked heatmap
            method = options.get('heatmap_method', 'kde')
            cell_size = options.get('cell_size', 50)

            result = generator.generate_masked_heatmap(
                points=points,
                values=values,
                mask_polygon=mask_polygon,
                method=method,
                cell_size=cell_size,
                classification_scheme=classification_scheme,
                map_type=layer_name.lower()
            )

            if 'error' in result:
                self.warnings.append(f"{layer_name}: {result['error']}")
                return None

            # Return the vector layer if available
            return result.get('vector_layer')

        except ImportError as e:
            self.warnings.append(f"Heatmap generator not available: {e}")
            return None
        except Exception as e:
            self.warnings.append(f"{layer_name} generation error: {e}")
            return None

    def _save_layer_to_gpkg(self, layer, layer_name, create_new=False):
        """
        Save a layer to the GeoPackage.

        Args:
            layer: QgsVectorLayer to save
            layer_name: Name for the layer in GeoPackage
            create_new: If True, create new file (for first layer)
        """
        if not layer or not layer.isValid():
            self.warnings.append(f"Cannot save invalid layer: {layer_name}")
            return False

        # Configure save options
        options = QgsVectorFileWriter.SaveVectorOptions()
        options.driverName = 'GPKG'
        options.layerName = layer_name

        if create_new:
            options.actionOnExistingFile = QgsVectorFileWriter.CreateOrOverwriteFile
        else:
            options.actionOnExistingFile = QgsVectorFileWriter.CreateOrOverwriteLayer

        # Transform context
        transform_context = QgsProject.instance().transformContext()

        # Write layer
        error = QgsVectorFileWriter.writeAsVectorFormatV3(
            layer,
            self.output_path,
            transform_context,
            options
        )

        if error[0] != QgsVectorFileWriter.NoError:
            self.errors.append(f"Error saving {layer_name}: {error[1]}")
            return False

        return True

    def _generate_project_code(self):
        """
        Generate a GNA project code (CPR) from project name.

        Max 20 characters, alphanumeric only.
        """
        import re
        # Clean project name
        code = re.sub(r'[^A-Za-z0-9]', '', self.project_name)
        # Uppercase and truncate
        code = code.upper()[:15]
        # Add timestamp suffix for uniqueness
        timestamp = datetime.now().strftime('%y%m')
        return f"{code}{timestamp}"[:20]

    def _log(self, message, level=None):
        """Log message to QGIS."""
        try:
            QgsMessageLog.logMessage(
                message,
                "PyArchInit GNA Export",
                level or Qgis.Info
            )
        except:
            pass  # Logging is optional

    @staticmethod
    def validate_geopackage(gpkg_path):
        """
        Validate a GNA GeoPackage for completeness.

        Args:
            gpkg_path: Path to GeoPackage file

        Returns:
            Dict with validation results
        """
        results = {
            'valid': True,
            'layers_found': [],
            'layers_missing': [],
            'errors': [],
            'warnings': [],
        }

        required_layers = ['MOPR']
        optional_layers = ['MOSI_point', 'MOSI_polygon', 'VRP', 'VRD']

        if not os.path.exists(gpkg_path):
            results['valid'] = False
            results['errors'].append(f"File not found: {gpkg_path}")
            return results

        try:
            # Try to open each layer
            for layer_name in required_layers + optional_layers:
                uri = f"{gpkg_path}|layername={layer_name}"
                layer = QgsVectorLayer(uri, layer_name, 'ogr')

                if layer.isValid():
                    results['layers_found'].append(layer_name)
                elif layer_name in required_layers:
                    results['layers_missing'].append(layer_name)
                    results['valid'] = False
                    results['errors'].append(f"Required layer missing: {layer_name}")

        except Exception as e:
            results['valid'] = False
            results['errors'].append(f"Validation error: {e}")

        return results
