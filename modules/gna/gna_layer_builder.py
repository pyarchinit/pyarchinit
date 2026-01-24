# -*- coding: utf-8 -*-
"""
GNA Layer Builder

Builds GNA-compliant vector layers for GeoPackage export:
- MOPR: Project perimeter (area of study)
- MOSI: Archaeological sites/findings (points and polygons)
- VRP: Archaeological potential map (classified multipolygon)
- VRD: Archaeological risk map (classified multipolygon)
"""

from qgis.core import (
    QgsVectorLayer,
    QgsField,
    QgsFeature,
    QgsGeometry,
    QgsFields,
    QgsCoordinateReferenceSystem,
    QgsCoordinateTransform,
    QgsProject,
    QgsWkbTypes
)
from qgis.PyQt.QtCore import QVariant

from .gna_field_mapper import GNAFieldMapper
from .gna_vocabulary_mapper import GNAVocabularyMapper


class GNALayerBuilder:
    """
    Builds GNA-compliant layers for archaeological data export.

    GNA Template Structure:
    - MOPR: Perimeter of the project (Polygon)
    - MOSI: Archaeological emergencies (Point/Polygon)
    - RCG: Survey areas (optional, MultiPolygon)
    - VRP: Potential risk valuation map (MultiPolygon, 5 classes)
    - VRD: Direct risk valuation map (MultiPolygon, 4 classes)
    """

    # MOPR field schema
    MOPR_FIELDS = [
        ('CPR', QVariant.String, 20),       # Project code (required)
        ('TITOLO', QVariant.String, 500),   # Project title
        ('RESPONSABILE', QVariant.String, 200),
        ('DATA_INIZIO', QVariant.String, 10),
        ('DATA_FINE', QVariant.String, 10),
        ('NOTE', QVariant.String, 5000),
        ('AREA_MQ', QVariant.Double, 0),    # Area in square meters
    ]

    # MOSI field schema (simplified, main fields)
    MOSI_FIELDS = [
        ('ID', QVariant.String, 10),        # Required, max 10 chars
        ('AMA', QVariant.String, 5),        # Site type (vocabulary)
        ('OGD', QVariant.String, 500),      # Object definition
        ('OGT', QVariant.String, 5),        # Geometry type
        ('DES', QVariant.String, 10000),    # Description
        ('OGM', QVariant.String, 200),      # Discovery method
        ('DTSI', QVariant.String, 20),      # Start date
        ('DTSF', QVariant.String, 20),      # End date
        ('DTSV', QVariant.String, 100),     # Start date validity
        ('DTSL', QVariant.String, 100),     # End date validity
        ('PRVN', QVariant.String, 100),     # Nation
        ('PVCR', QVariant.String, 100),     # Region
        ('PVCP', QVariant.String, 5),       # Province code
        ('PVCC', QVariant.String, 200),     # Municipality
        ('PVCF', QVariant.String, 200),     # Fraction
        ('LCGG', QVariant.String, 50),      # Geographic coordinates
        ('LCDQ', QVariant.Double, 0),       # Elevation
        ('MTDM', QVariant.String, 5),       # Survey method
        ('VGTC', QVariant.String, 5),       # Vegetation coverage
        ('GPMT', QVariant.String, 5),       # GPS method
        ('MCND', QVariant.String, 5),       # Surface condition
        ('ACCB', QVariant.String, 5),       # Accessibility
        ('WTHR', QVariant.String, 5),       # Weather
        ('VCND', QVariant.Int, 0),          # Visibility percent
        ('RSPR', QVariant.String, 200),     # Responsible
        ('DTRR', QVariant.String, 10),      # Survey date
        ('BIBR', QVariant.String, 5000),    # Bibliography
    ]

    # VRP/VRD field schema
    VR_FIELDS = [
        ('CLASSE', QVariant.String, 2),     # Class code (NV, NU, BA, ME, AL)
        ('LABEL', QVariant.String, 50),     # Class label
        ('VALORE_MIN', QVariant.Double, 0),
        ('VALORE_MAX', QVariant.Double, 0),
        ('COLORE', QVariant.String, 7),     # Hex color
        ('AREA_MQ', QVariant.Double, 0),    # Area in square meters
    ]

    def __init__(self, crs=None, language='it'):
        """
        Initialize layer builder.

        Args:
            crs: QgsCoordinateReferenceSystem for output layers
            language: Language code for vocabulary translations
        """
        self.crs = crs or QgsCoordinateReferenceSystem('EPSG:4326')
        self.language = language
        self.field_mapper = GNAFieldMapper(language)
        self.vocab_mapper = GNAVocabularyMapper(language)

    def build_mopr_layer(self, polygon_geometry, project_info):
        """
        Build MOPR (project perimeter) layer.

        Args:
            polygon_geometry: QgsGeometry of the project area
            project_info: Dict with project metadata (code, title, responsible, etc.)

        Returns:
            QgsVectorLayer with single MOPR feature
        """
        crs_string = self.crs.authid()
        layer = QgsVectorLayer(
            f'Polygon?crs={crs_string}',
            'MOPR',
            'memory'
        )

        # Add fields
        fields = self._create_fields(self.MOPR_FIELDS)
        layer.dataProvider().addAttributes(fields)
        layer.updateFields()

        # Map project info to MOPR fields
        mopr_data = self.field_mapper.get_mopr_fields(project_info)

        # Create feature
        feat = QgsFeature()
        feat.setGeometry(polygon_geometry)

        # Calculate area
        area = polygon_geometry.area()

        # Set attributes
        feat.setAttributes([
            mopr_data.get('CPR', ''),
            mopr_data.get('TITOLO', ''),
            mopr_data.get('RESPONSABILE', ''),
            mopr_data.get('DATA_INIZIO', ''),
            mopr_data.get('DATA_FINE', ''),
            mopr_data.get('NOTE', ''),
            float(area),
        ])

        layer.dataProvider().addFeature(feat)
        layer.updateExtents()

        return layer

    def build_mosi_layers(self, ut_records, geometries=None):
        """
        Build MOSI layers (point and polygon) from UT records.

        Args:
            ut_records: List of UT database records
            geometries: Optional dict mapping record ID to QgsGeometry

        Returns:
            Dict with 'point_layer' and 'polygon_layer' QgsVectorLayers
        """
        geometries = geometries or {}
        crs_string = self.crs.authid()

        # Create point layer
        point_layer = QgsVectorLayer(
            f'Point?crs={crs_string}',
            'MOSI_point',
            'memory'
        )

        # Create polygon layer
        polygon_layer = QgsVectorLayer(
            f'Polygon?crs={crs_string}',
            'MOSI_polygon',
            'memory'
        )

        # Add fields to both layers
        fields = self._create_fields(self.MOSI_FIELDS)
        point_layer.dataProvider().addAttributes(fields)
        polygon_layer.dataProvider().addAttributes(fields)
        point_layer.updateFields()
        polygon_layer.updateFields()

        point_features = []
        polygon_features = []

        for record in ut_records:
            # Get geometry
            record_id = getattr(record, 'id_ut', None) or getattr(record, 'nr_ut', None)
            geom = geometries.get(record_id)

            # Try to create point geometry from coordinates if no geometry provided
            if not geom:
                geom = self._create_geometry_from_record(record)

            if not geom:
                continue

            # Map UT record to MOSI fields
            mosi_data = self.field_mapper.map_ut_record_to_mosi(record, geom)

            # Create feature
            feat = QgsFeature()
            feat.setGeometry(geom)

            # Set attributes in field order
            attributes = self._mosi_data_to_attributes(mosi_data)
            feat.setAttributes(attributes)

            # Add to appropriate layer based on geometry type
            if geom.type() == QgsWkbTypes.PointGeometry:
                point_features.append(feat)
            elif geom.type() == QgsWkbTypes.PolygonGeometry:
                polygon_features.append(feat)

        # Add features to layers
        if point_features:
            point_layer.dataProvider().addFeatures(point_features)
            point_layer.updateExtents()

        if polygon_features:
            polygon_layer.dataProvider().addFeatures(polygon_features)
            polygon_layer.updateExtents()

        return {
            'point_layer': point_layer if point_features else None,
            'polygon_layer': polygon_layer if polygon_features else None,
        }

    def build_vr_layer(self, classified_geometries, layer_name, vr_type='vrp'):
        """
        Build VRP or VRD layer from pre-classified geometries.

        Args:
            classified_geometries: List of dicts with:
                - geometry: QgsGeometry (multipolygon)
                - code: Class code
                - label: Class label
                - min_value: Minimum value
                - max_value: Maximum value
                - color: Hex color
            layer_name: Name for the layer
            vr_type: 'vrp' or 'vrd'

        Returns:
            QgsVectorLayer with classified features
        """
        crs_string = self.crs.authid()
        layer = QgsVectorLayer(
            f'MultiPolygon?crs={crs_string}',
            layer_name,
            'memory'
        )

        # Add fields
        fields = self._create_fields(self.VR_FIELDS)
        layer.dataProvider().addAttributes(fields)
        layer.updateFields()

        features = []
        for class_data in classified_geometries:
            geom = class_data.get('geometry')
            if not geom or geom.isEmpty():
                continue

            feat = QgsFeature()
            feat.setGeometry(geom)

            # Calculate area
            area = geom.area()

            feat.setAttributes([
                class_data.get('code', ''),
                class_data.get('label', ''),
                float(class_data.get('min_value', 0)),
                float(class_data.get('max_value', 100)),
                class_data.get('color', '#808080'),
                float(area),
            ])
            features.append(feat)

        if features:
            layer.dataProvider().addFeatures(features)
            layer.updateExtents()

        return layer

    def _create_fields(self, field_schema):
        """
        Create QgsFields from field schema.

        Args:
            field_schema: List of (name, type, length) tuples

        Returns:
            List of QgsField objects
        """
        fields = []
        for name, qtype, length in field_schema:
            field = QgsField(name, qtype)
            if length > 0 and qtype == QVariant.String:
                field.setLength(length)
            fields.append(field)
        return fields

    def _create_geometry_from_record(self, record):
        """
        Create geometry from UT record coordinate fields.

        Args:
            record: UT database record

        Returns:
            QgsGeometry or None
        """
        from qgis.core import QgsPointXY

        # Try coord_piane first (UTM or projected)
        coord_piane = getattr(record, 'coord_piane', None)
        if coord_piane:
            try:
                parts = str(coord_piane).replace(';', ',').split(',')
                if len(parts) >= 2:
                    x = float(parts[0].strip())
                    y = float(parts[1].strip())
                    return QgsGeometry.fromPointXY(QgsPointXY(x, y))
            except (ValueError, TypeError):
                pass

        # Try coord_geografiche (lat/lon)
        coord_geo = getattr(record, 'coord_geografiche', None)
        if coord_geo:
            try:
                parts = str(coord_geo).replace(';', ',').split(',')
                if len(parts) >= 2:
                    # Assuming lat, lon order
                    lat = float(parts[0].strip())
                    lon = float(parts[1].strip())

                    # Create point in WGS84
                    point = QgsGeometry.fromPointXY(QgsPointXY(lon, lat))

                    # Transform to target CRS if different
                    if self.crs.authid() != 'EPSG:4326':
                        transform = QgsCoordinateTransform(
                            QgsCoordinateReferenceSystem('EPSG:4326'),
                            self.crs,
                            QgsProject.instance()
                        )
                        point.transform(transform)

                    return point
            except (ValueError, TypeError):
                pass

        return None

    def _mosi_data_to_attributes(self, mosi_data):
        """
        Convert MOSI data dict to attributes list in field order.

        Args:
            mosi_data: Dict from field_mapper.map_ut_record_to_mosi()

        Returns:
            List of attribute values in MOSI_FIELDS order
        """
        attributes = []
        for field_name, _, _ in self.MOSI_FIELDS:
            value = mosi_data.get(field_name, '')
            if value is None:
                value = ''
            attributes.append(value)
        return attributes

    def style_vrp_layer(self, layer):
        """
        Apply VRP classification styling to layer.

        Args:
            layer: QgsVectorLayer with CLASSE and COLORE fields
        """
        self._apply_categorized_style(layer, 'VRP')

    def style_vrd_layer(self, layer):
        """
        Apply VRD classification styling to layer.

        Args:
            layer: QgsVectorLayer with CLASSE and COLORE fields
        """
        self._apply_categorized_style(layer, 'VRD')

    def _apply_categorized_style(self, layer, layer_type):
        """
        Apply categorized style based on CLASSE field.

        Args:
            layer: QgsVectorLayer
            layer_type: 'VRP' or 'VRD'
        """
        try:
            from qgis.core import (
                QgsCategorizedSymbolRenderer,
                QgsRendererCategory,
                QgsFillSymbol
            )

            renderer = QgsCategorizedSymbolRenderer('CLASSE')

            # Get unique classes from layer
            classes = set()
            for feat in layer.getFeatures():
                classe = feat['CLASSE']
                color = feat['COLORE']
                label = feat['LABEL']
                if classe:
                    classes.add((classe, color, label))

            for classe, color, label in sorted(classes, key=lambda x: x[0]):
                symbol = QgsFillSymbol.createSimple({
                    'color': color,
                    'outline_color': '#333333',
                    'outline_width': '0.5'
                })

                category = QgsRendererCategory(classe, symbol, f"{classe} - {label}")
                renderer.addCategory(category)

            layer.setRenderer(renderer)
            layer.triggerRepaint()

        except Exception as e:
            pass  # Styling is optional, don't fail export

    def validate_layer(self, layer, layer_type):
        """
        Validate a GNA layer for completeness.

        Args:
            layer: QgsVectorLayer
            layer_type: 'MOPR', 'MOSI', 'VRP', or 'VRD'

        Returns:
            Dict with 'valid' bool and 'errors' list
        """
        errors = []

        if not layer or not layer.isValid():
            return {'valid': False, 'errors': ['Layer non valido']}

        feature_count = layer.featureCount()
        if feature_count == 0:
            errors.append(f'Layer {layer_type} vuoto')

        # Check required fields based on layer type
        if layer_type == 'MOPR':
            required = ['CPR']
        elif layer_type == 'MOSI':
            required = ['ID', 'AMA', 'OGD']
        elif layer_type in ('VRP', 'VRD'):
            required = ['CLASSE']
        else:
            required = []

        field_names = [f.name() for f in layer.fields()]
        for req_field in required:
            if req_field not in field_names:
                errors.append(f'Campo obbligatorio mancante: {req_field}')

        # Check for empty required values
        for feat in layer.getFeatures():
            for req_field in required:
                if req_field in field_names:
                    value = feat[req_field]
                    if not value or (isinstance(value, str) and not value.strip()):
                        errors.append(
                            f'Valore mancante per {req_field} in feature {feat.id()}'
                        )
                        break  # Only report first error per feature

        return {
            'valid': len(errors) == 0,
            'errors': errors,
        }
