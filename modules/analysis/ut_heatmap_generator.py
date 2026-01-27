#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
UT Heatmap Generator - Generates archaeological potential and risk heatmaps.

Supports three methods:
- Kernel Density Estimation (KDE): Smooth continuous surface
- Inverse Distance Weighting (IDW): Value interpolation
- Grid-Based Aggregation: Cell-based statistics

Created for PyArchInit QGIS Plugin
"""

import os
import tempfile
import json
from datetime import datetime

# Numpy import with comprehensive error handling
# The _ARRAY_API error occurs when numpy's C module has version mismatch
NUMPY_AVAILABLE = False
np = None
try:
    import numpy as np
    # Test if numpy array API is working
    _ = np.array([1, 2, 3])
    NUMPY_AVAILABLE = True
except (ImportError, AttributeError, Exception) as e:
    # Catch any error including _ARRAY_API issues
    NUMPY_AVAILABLE = False
    np = None

# Scipy import
SCIPY_AVAILABLE = False
try:
    if NUMPY_AVAILABLE:
        from scipy import stats
        from scipy.interpolate import griddata
        SCIPY_AVAILABLE = True
except (ImportError, Exception):
    SCIPY_AVAILABLE = False

# GDAL import with array support check
GDAL_AVAILABLE = False
GDAL_ARRAY_AVAILABLE = False
try:
    from osgeo import gdal, osr
    GDAL_AVAILABLE = True
    # Test if GDAL array support is working
    try:
        from osgeo import gdal_array
        GDAL_ARRAY_AVAILABLE = True
    except (ImportError, Exception):
        GDAL_ARRAY_AVAILABLE = False
except (ImportError, Exception):
    GDAL_AVAILABLE = False
    GDAL_ARRAY_AVAILABLE = False

try:
    from qgis.core import (
        QgsProject,
        QgsVectorLayer,
        QgsRasterLayer,
        QgsField,
        QgsFeature,
        QgsGeometry,
        QgsPointXY,
        QgsRectangle,
        QgsCoordinateReferenceSystem,
        QgsRasterBandStats,
        QgsColorRampShader,
        QgsRasterShader,
        QgsSingleBandPseudoColorRenderer,
        QgsGradientColorRamp,
        QgsMessageLog,
        Qgis,
        QgsFields
    )
    from qgis.PyQt.QtCore import QVariant
    from qgis.PyQt.QtGui import QColor
    QGIS_AVAILABLE = True
except ImportError:
    QGIS_AVAILABLE = False


class UTHeatmapGenerator:
    """
    Generates heatmaps for archaeological potential and risk analysis.

    Supports three interpolation methods:
    - KDE (Kernel Density Estimation): Best for density visualization
    - IDW (Inverse Distance Weighting): Best for value interpolation
    - Grid: Best for simple aggregation visualization
    """

    # Default parameters
    DEFAULT_CELL_SIZE = 50  # meters
    DEFAULT_BANDWIDTH = 'auto'
    DEFAULT_IDW_POWER = 2
    DEFAULT_SEARCH_RADIUS = None  # Use all points

    # Color ramps for different map types
    POTENTIAL_COLORS = [
        (0, '#2ECC71'),     # Green - low potential
        (25, '#F1C40F'),    # Yellow
        (50, '#E67E22'),    # Orange
        (75, '#E74C3C'),    # Red
        (100, '#8E44AD')    # Purple - high potential
    ]

    RISK_COLORS = [
        (0, '#2ECC71'),     # Green - low risk
        (25, '#F1C40F'),    # Yellow
        (50, '#E67E22'),    # Orange
        (75, '#E74C3C'),    # Red
        (100, '#C0392B')    # Dark red - high risk
    ]

    def __init__(self, output_dir=None, crs=None):
        """
        Initialize the heatmap generator.

        Args:
            output_dir: Directory for output files (default: temp dir)
            crs: Coordinate Reference System (QgsCoordinateReferenceSystem)
        """
        self.output_dir = output_dir or tempfile.gettempdir()
        self.crs = crs
        self._check_dependencies()

    def _check_dependencies(self):
        """Check for required dependencies."""
        self.has_numpy = NUMPY_AVAILABLE
        self.has_scipy = SCIPY_AVAILABLE
        self.has_gdal = GDAL_AVAILABLE
        self.has_gdal_array = GDAL_ARRAY_AVAILABLE
        self.has_qgis = QGIS_AVAILABLE

        if not self.has_numpy:
            self.log_message("NumPy not available - using simplified heatmap generation")
        if not self.has_gdal_array:
            self.log_message("GDAL array not available - using vector-based heatmaps")

    def log_message(self, message, level=None):
        """Log message to QGIS if available."""
        if QGIS_AVAILABLE:
            QgsMessageLog.logMessage(
                message,
                "PyArchInit Heatmap",
                level or Qgis.Info
            )

    def generate_heatmap(self, points, values, method='kde',
                        cell_size=None, bandwidth=None,
                        power=None, search_radius=None,
                        extent=None, map_type='potential'):
        """
        Generate a heatmap using the specified method.

        Args:
            points: List of (x, y) coordinate tuples
            values: List of values corresponding to each point
            method: 'kde', 'idw', or 'grid'
            cell_size: Grid cell size in map units
            bandwidth: KDE bandwidth (or 'auto')
            power: IDW power parameter
            search_radius: Maximum search radius for IDW
            extent: (xmin, ymin, xmax, ymax) or QgsRectangle
            map_type: 'potential' or 'risk' (for color styling)

        Returns:
            Dictionary with:
                - raster_path: Path to output GeoTIFF
                - layer: QgsRasterLayer (if QGIS available)
                - stats: Statistics dictionary
                - method: Method used
                - timestamp: Generation timestamp
        """
        if not points or not values:
            return {'error': 'No points or values provided'}

        # If numpy not available or GDAL array not working, use vector grid approach
        if not self.has_numpy or not self.has_gdal_array:
            return self.generate_vector_grid(
                points, values,
                cell_size or self.DEFAULT_CELL_SIZE,
                extent,
                'score',
                map_type
            )

        # Convert inputs to numpy arrays
        points = np.array(points)
        values = np.array(values)

        # Use defaults for optional parameters
        cell_size = cell_size or self.DEFAULT_CELL_SIZE
        bandwidth = bandwidth or self.DEFAULT_BANDWIDTH
        power = power or self.DEFAULT_IDW_POWER
        search_radius = search_radius if search_radius else self.DEFAULT_SEARCH_RADIUS

        # Calculate extent if not provided
        if extent is None:
            margin = cell_size * 5
            extent = (
                points[:, 0].min() - margin,
                points[:, 1].min() - margin,
                points[:, 0].max() + margin,
                points[:, 1].max() + margin
            )
        elif self.has_qgis and isinstance(extent, QgsRectangle):
            extent = (extent.xMinimum(), extent.yMinimum(),
                     extent.xMaximum(), extent.yMaximum())

        # Generate heatmap based on method
        try:
            if method.lower() == 'kde':
                grid, grid_extent = self._generate_kde(
                    points, values, cell_size, bandwidth, extent
                )
            elif method.lower() == 'idw':
                grid, grid_extent = self._generate_idw(
                    points, values, cell_size, power, search_radius, extent
                )
            elif method.lower() == 'grid':
                grid, grid_extent = self._generate_grid(
                    points, values, cell_size, extent
                )
            else:
                return {'error': f'Unknown method: {method}'}

            # Save as GeoTIFF
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"ut_{map_type}_{method}_{timestamp}.tif"
            raster_path = os.path.join(self.output_dir, filename)

            self._save_geotiff(grid, grid_extent, raster_path, cell_size)

            # Calculate statistics
            stats = {
                'min': float(np.nanmin(grid)),
                'max': float(np.nanmax(grid)),
                'mean': float(np.nanmean(grid)),
                'std': float(np.nanstd(grid)),
                'count': int(np.sum(~np.isnan(grid)))
            }

            result = {
                'raster_path': raster_path,
                'stats': stats,
                'method': method,
                'cell_size': cell_size,
                'extent': grid_extent,
                'timestamp': datetime.now().isoformat()
            }

            # Create QGIS layer if available
            if self.has_qgis:
                layer = self._create_styled_layer(
                    raster_path,
                    f"UT {map_type.capitalize()} ({method.upper()})",
                    map_type
                )
                result['layer'] = layer

            return result

        except Exception as e:
            self.log_message(f"Heatmap generation error: {e}", Qgis.Warning if QGIS_AVAILABLE else None)
            return {'error': str(e)}

    def _generate_kde(self, points, values, cell_size, bandwidth, extent):
        """
        Generate heatmap using Kernel Density Estimation.

        Args:
            points: Nx2 array of coordinates
            values: N array of values
            cell_size: Grid cell size
            bandwidth: KDE bandwidth or 'auto'
            extent: (xmin, ymin, xmax, ymax)

        Returns:
            Tuple of (grid array, extent)
        """
        if not self.has_scipy:
            # Fallback to simple binning if scipy not available
            return self._generate_grid(points, values, cell_size, extent)

        xmin, ymin, xmax, ymax = extent

        # Create grid
        nx = int((xmax - xmin) / cell_size)
        ny = int((ymax - ymin) / cell_size)

        if nx <= 0 or ny <= 0:
            nx = max(1, nx)
            ny = max(1, ny)

        xi = np.linspace(xmin, xmax, nx)
        yi = np.linspace(ymin, ymax, ny)
        xi, yi = np.meshgrid(xi, yi)

        # Prepare positions for evaluation
        positions = np.vstack([xi.ravel(), yi.ravel()])

        # Weighted KDE using point values as weights
        try:
            if bandwidth == 'auto':
                kernel = stats.gaussian_kde(points.T, weights=values)
            else:
                kernel = stats.gaussian_kde(points.T, weights=values, bw_method=bandwidth)

            z = np.reshape(kernel(positions), xi.shape)

            # Normalize to 0-100 scale based on value range
            if z.max() > z.min():
                z = ((z - z.min()) / (z.max() - z.min())) * 100

        except Exception as e:
            self.log_message(f"KDE calculation error: {e}, using grid fallback")
            return self._generate_grid(points, values, cell_size, extent)

        return z, extent

    def _generate_idw(self, points, values, cell_size, power, search_radius, extent):
        """
        Generate heatmap using Inverse Distance Weighting.

        Args:
            points: Nx2 array of coordinates
            values: N array of values
            cell_size: Grid cell size
            power: IDW power parameter
            search_radius: Maximum search radius
            extent: (xmin, ymin, xmax, ymax)

        Returns:
            Tuple of (grid array, extent)
        """
        xmin, ymin, xmax, ymax = extent

        # Create grid
        nx = int((xmax - xmin) / cell_size)
        ny = int((ymax - ymin) / cell_size)

        if nx <= 0 or ny <= 0:
            nx = max(1, nx)
            ny = max(1, ny)

        xi = np.linspace(xmin + cell_size/2, xmax - cell_size/2, nx)
        yi = np.linspace(ymin + cell_size/2, ymax - cell_size/2, ny)
        xi, yi = np.meshgrid(xi, yi)

        grid = np.zeros_like(xi)

        # IDW interpolation
        for i in range(ny):
            for j in range(nx):
                px, py = xi[i, j], yi[i, j]

                # Calculate distances to all points
                distances = np.sqrt((points[:, 0] - px)**2 + (points[:, 1] - py)**2)

                # Apply search radius if specified
                if search_radius:
                    mask = distances <= search_radius
                    if not np.any(mask):
                        grid[i, j] = np.nan
                        continue
                    distances = distances[mask]
                    v = values[mask]
                else:
                    v = values

                # Handle zero distances
                zero_dist = distances == 0
                if np.any(zero_dist):
                    grid[i, j] = v[zero_dist][0]
                else:
                    # IDW formula
                    weights = 1 / (distances ** power)
                    grid[i, j] = np.sum(weights * v) / np.sum(weights)

        return grid, extent

    def _generate_grid(self, points, values, cell_size, extent):
        """
        Generate heatmap using simple grid-based aggregation.

        Args:
            points: Nx2 array of coordinates
            values: N array of values
            cell_size: Grid cell size
            extent: (xmin, ymin, xmax, ymax)

        Returns:
            Tuple of (grid array, extent)
        """
        xmin, ymin, xmax, ymax = extent

        # Create grid
        nx = int((xmax - xmin) / cell_size)
        ny = int((ymax - ymin) / cell_size)

        if nx <= 0 or ny <= 0:
            nx = max(1, nx)
            ny = max(1, ny)

        # Initialize grids for sum and count
        grid_sum = np.zeros((ny, nx))
        grid_count = np.zeros((ny, nx))

        # Assign points to cells
        for (x, y), v in zip(points, values):
            ix = int((x - xmin) / cell_size)
            iy = int((y - ymin) / cell_size)

            # Clamp to grid bounds
            ix = max(0, min(nx - 1, ix))
            iy = max(0, min(ny - 1, iy))

            grid_sum[iy, ix] += v
            grid_count[iy, ix] += 1

        # Calculate mean (avoid division by zero)
        with np.errstate(divide='ignore', invalid='ignore'):
            grid = np.where(grid_count > 0, grid_sum / grid_count, np.nan)

        return grid, extent

    def _save_geotiff(self, grid, extent, filepath, cell_size):
        """
        Save grid as GeoTIFF file.

        Args:
            grid: 2D numpy array
            extent: (xmin, ymin, xmax, ymax)
            filepath: Output file path
            cell_size: Cell size for geotransform
        """
        if not self.has_gdal:
            # Fallback: save as numpy file
            np.save(filepath.replace('.tif', '.npy'), grid)
            self.log_message("GDAL not available, saved as .npy")
            return

        xmin, ymin, xmax, ymax = extent
        ny, nx = grid.shape

        # Create GeoTIFF
        driver = gdal.GetDriverByName('GTiff')
        dataset = driver.Create(filepath, nx, ny, 1, gdal.GDT_Float32)

        # Set geotransform
        # (xmin, pixel_width, 0, ymax, 0, -pixel_height)
        pixel_width = (xmax - xmin) / nx
        pixel_height = (ymax - ymin) / ny
        dataset.SetGeoTransform((xmin, pixel_width, 0, ymax, 0, -pixel_height))

        # Set projection if available
        if self.crs:
            srs = osr.SpatialReference()
            if self.has_qgis and isinstance(self.crs, QgsCoordinateReferenceSystem):
                srs.ImportFromWkt(self.crs.toWkt())
            else:
                srs.ImportFromEPSG(32632)  # Default UTM 32N
            dataset.SetProjection(srs.ExportToWkt())

        # Write data (flip vertically for correct orientation)
        band = dataset.GetRasterBand(1)
        band.WriteArray(grid[::-1])
        band.SetNoDataValue(-9999)

        # Replace NaN with nodata
        grid_cleaned = np.where(np.isnan(grid), -9999, grid)
        band.WriteArray(grid_cleaned[::-1])

        band.FlushCache()
        dataset = None

    def _create_styled_layer(self, raster_path, layer_name, map_type='potential'):
        """
        Create a styled QGIS raster layer.

        Args:
            raster_path: Path to GeoTIFF
            layer_name: Name for the layer
            map_type: 'potential' or 'risk' for color styling

        Returns:
            QgsRasterLayer
        """
        if not self.has_qgis:
            return None

        layer = QgsRasterLayer(raster_path, layer_name)

        if not layer.isValid():
            self.log_message(f"Failed to create layer from {raster_path}")
            return None

        # Get color ramp based on map type
        colors = self.POTENTIAL_COLORS if map_type == 'potential' else self.RISK_COLORS

        # Create color ramp shader
        shader = QgsRasterShader()
        color_ramp = QgsColorRampShader()
        color_ramp.setColorRampType(QgsColorRampShader.Interpolated)

        # Create color ramp items
        ramp_items = []
        for value, hex_color in colors:
            color = QColor(hex_color)
            ramp_items.append(QgsColorRampShader.ColorRampItem(value, color))

        color_ramp.setColorRampItemList(ramp_items)
        shader.setRasterShaderFunction(color_ramp)

        # Apply renderer
        renderer = QgsSingleBandPseudoColorRenderer(layer.dataProvider(), 1, shader)
        layer.setRenderer(renderer)

        layer.triggerRepaint()

        return layer

    def generate_vector_grid(self, points, values, cell_size, extent=None,
                            value_field='score', map_type='potential'):
        """
        Generate a vector grid layer with aggregated values per cell.

        Args:
            points: List of (x, y) coordinate tuples
            values: List of values corresponding to each point
            cell_size: Grid cell size in map units
            extent: (xmin, ymin, xmax, ymax) or None to auto-calculate
            value_field: Name of the value field
            map_type: 'potential' or 'risk'

        Returns:
            Dictionary with:
                - layer: QgsVectorLayer (memory layer)
                - stats: Statistics dictionary
                - cell_count: Number of cells with data
        """
        if not self.has_qgis:
            return {'error': 'QGIS required for vector grid generation'}

        # Convert to list if numpy arrays
        if self.has_numpy:
            import numpy as np
            if isinstance(points, np.ndarray):
                points = points.tolist()
            if isinstance(values, np.ndarray):
                values = values.tolist()

        # Calculate extent from points
        if extent is None:
            margin = cell_size * 2
            x_coords = [p[0] for p in points]
            y_coords = [p[1] for p in points]
            extent = (
                min(x_coords) - margin,
                min(y_coords) - margin,
                max(x_coords) + margin,
                max(y_coords) + margin
            )

        xmin, ymin, xmax, ymax = extent

        # Create memory layer
        crs_string = self.crs.authid() if self.crs else 'EPSG:4326'
        layer = QgsVectorLayer(f'Polygon?crs={crs_string}',
                              f'UT {map_type.capitalize()} Grid', 'memory')
        provider = layer.dataProvider()

        # Add fields
        fields = QgsFields()
        fields.append(QgsField(value_field, QVariant.Double))
        fields.append(QgsField('count', QVariant.Int))
        fields.append(QgsField('cell_x', QVariant.Int))
        fields.append(QgsField('cell_y', QVariant.Int))
        provider.addAttributes(fields)
        layer.updateFields()

        # Generate grid cells
        nx = int((xmax - xmin) / cell_size) + 1
        ny = int((ymax - ymin) / cell_size) + 1

        # Aggregate points into cells
        cell_data = {}
        for (x, y), v in zip(points, values):
            ix = int((x - xmin) / cell_size)
            iy = int((y - ymin) / cell_size)
            key = (ix, iy)

            if key not in cell_data:
                cell_data[key] = []
            cell_data[key].append(v)

        # Create features for cells with data
        features = []
        for (ix, iy), cell_values in cell_data.items():
            # Cell bounds
            cx = xmin + ix * cell_size
            cy = ymin + iy * cell_size

            # Create polygon
            poly = QgsGeometry.fromPolygonXY([[
                QgsPointXY(cx, cy),
                QgsPointXY(cx + cell_size, cy),
                QgsPointXY(cx + cell_size, cy + cell_size),
                QgsPointXY(cx, cy + cell_size),
                QgsPointXY(cx, cy)
            ]])

            # Create feature
            feat = QgsFeature()
            feat.setGeometry(poly)
            # Calculate mean without numpy
            cell_mean = sum(cell_values) / len(cell_values) if cell_values else 0
            feat.setAttributes([
                float(cell_mean),
                len(cell_values),
                ix,
                iy
            ])
            features.append(feat)

        provider.addFeatures(features)

        # Apply styling
        self._style_vector_grid(layer, value_field, map_type)

        # Calculate statistics without numpy
        all_values = [v for vals in cell_data.values() for v in vals]
        stats = {
            'min': float(min(all_values)) if all_values else 0,
            'max': float(max(all_values)) if all_values else 0,
            'mean': float(sum(all_values) / len(all_values)) if all_values else 0,
            'cells_with_data': len(cell_data)
        }

        return {
            'layer': layer,
            'stats': stats,
            'cell_count': len(cell_data)
        }

    def _style_vector_grid(self, layer, value_field, map_type='potential'):
        """
        Apply graduated styling to vector grid layer.

        Args:
            layer: QgsVectorLayer
            value_field: Field name for values
            map_type: 'potential' or 'risk'
        """
        if not self.has_qgis:
            return

        try:
            from qgis.core import (
                QgsGraduatedSymbolRenderer,
                QgsRendererRange,
                QgsSymbol,
                QgsStyle,
                QgsFillSymbol
            )

            colors = self.POTENTIAL_COLORS if map_type == 'potential' else self.RISK_COLORS

            # Create graduated renderer with manual ranges
            renderer = QgsGraduatedSymbolRenderer(value_field)

            # Create ranges based on color stops
            ranges = []
            for i in range(len(colors) - 1):
                lower_val, lower_color = colors[i]
                upper_val, upper_color = colors[i + 1]

                symbol = QgsFillSymbol.createSimple({
                    'color': lower_color,
                    'outline_color': '#666666',
                    'outline_width': '0.2'
                })

                range_obj = QgsRendererRange(
                    lower_val, upper_val,
                    symbol,
                    f'{lower_val}-{upper_val}'
                )
                ranges.append(range_obj)

            renderer.setClassAttribute(value_field)
            for r in ranges:
                renderer.addClassRange(r)

            layer.setRenderer(renderer)
            layer.triggerRepaint()

        except Exception as e:
            self.log_message(f"Error styling vector grid: {e}")

    # =========================================================================
    # GNA Polygon-Masked Heatmap Methods
    # =========================================================================

    def generate_masked_heatmap(self, points, values, mask_polygon,
                                 method='kde', cell_size=None,
                                 classification_scheme=None,
                                 map_type='potential'):
        """
        Generate a heatmap masked to an irregular polygon boundary (MOPR).

        This method is designed for GNA export, generating heatmaps that are
        clipped to the project area polygon and optionally classified into
        VRP/VRD categories.

        Args:
            points: List of (x, y) coordinate tuples
            values: List of values (potential_score or risk_score)
            mask_polygon: QgsGeometry of the project boundary (MOPR)
            method: 'kde', 'idw', or 'grid'
            cell_size: Grid cell size in map units (default 50m)
            classification_scheme: Dict for VRP/VRD classification:
                {(min, max): {'code': 'XX', 'label': '...', 'color': '#XXXXXX'}}
            map_type: 'potential' or 'risk' for styling

        Returns:
            Dictionary with:
                - raster_path: Path to masked GeoTIFF
                - vector_layer: Classified multipolygon layer (if scheme provided)
                - stats: Statistics dictionary
                - method: Method used
        """
        if not points or not values:
            return {'error': 'No points or values provided'}

        if not mask_polygon or mask_polygon.isEmpty():
            return {'error': 'Invalid mask polygon'}

        if not self.has_numpy:
            return {'error': 'NumPy required for masked heatmap generation'}

        cell_size = cell_size or self.DEFAULT_CELL_SIZE

        # Get extent from polygon bounding box
        bbox = mask_polygon.boundingBox()
        extent = (
            bbox.xMinimum(),
            bbox.yMinimum(),
            bbox.xMaximum(),
            bbox.yMaximum()
        )

        # Convert to numpy arrays
        points_array = np.array(points)
        values_array = np.array(values)

        try:
            # Generate heatmap grid
            if method.lower() == 'kde':
                grid, grid_extent = self._generate_kde(
                    points_array, values_array, cell_size, 'auto', extent
                )
            elif method.lower() == 'idw':
                grid, grid_extent = self._generate_idw(
                    points_array, values_array, cell_size,
                    self.DEFAULT_IDW_POWER, None, extent
                )
            elif method.lower() == 'grid':
                grid, grid_extent = self._generate_grid(
                    points_array, values_array, cell_size, extent
                )
            else:
                return {'error': f'Unknown method: {method}'}

            # Create mask from polygon
            mask_array = self._rasterize_polygon(mask_polygon, grid.shape, bbox)

            # Apply mask (values outside polygon become NaN)
            masked_grid = np.where(mask_array, grid, np.nan)

            # Save masked raster
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"gna_{map_type}_{method}_{timestamp}.tif"
            raster_path = os.path.join(self.output_dir, filename)

            self._save_geotiff(masked_grid, grid_extent, raster_path, cell_size)

            # Calculate statistics
            valid_values = masked_grid[~np.isnan(masked_grid)]
            stats = {
                'min': float(np.min(valid_values)) if len(valid_values) > 0 else 0,
                'max': float(np.max(valid_values)) if len(valid_values) > 0 else 0,
                'mean': float(np.mean(valid_values)) if len(valid_values) > 0 else 0,
                'std': float(np.std(valid_values)) if len(valid_values) > 0 else 0,
                'valid_cells': int(np.sum(~np.isnan(masked_grid))),
                'total_cells': int(masked_grid.size)
            }

            result = {
                'raster_path': raster_path,
                'stats': stats,
                'method': method,
                'cell_size': cell_size,
                'extent': grid_extent,
                'timestamp': datetime.now().isoformat()
            }

            # Classify and polygonize if scheme provided
            if classification_scheme:
                vector_layer = self._classify_to_multipolygon(
                    masked_grid, bbox, mask_polygon, classification_scheme, map_type
                )
                result['vector_layer'] = vector_layer

            # Create styled raster layer if QGIS available
            if self.has_qgis:
                layer = self._create_styled_layer(
                    raster_path,
                    f"GNA {map_type.capitalize()} ({method.upper()})",
                    map_type
                )
                result['raster_layer'] = layer

            return result

        except Exception as e:
            if QGIS_AVAILABLE:
                self.log_message(f"Masked heatmap error: {e}", Qgis.Warning)
            else:
                self.log_message(f"Masked heatmap error: {e}")
            return {'error': str(e)}

    def _rasterize_polygon(self, polygon, shape, extent):
        """
        Convert a QgsGeometry polygon to a boolean raster mask.

        Args:
            polygon: QgsGeometry polygon
            shape: Tuple (rows, cols) for output array shape
            extent: QgsRectangle of the grid extent

        Returns:
            Boolean numpy array where True = inside polygon
        """
        if not self.has_gdal:
            # Fallback: simple point-in-polygon test
            return self._rasterize_polygon_simple(polygon, shape, extent)

        from osgeo import gdal, ogr

        ny, nx = shape

        # Create in-memory raster
        driver = gdal.GetDriverByName('MEM')
        raster = driver.Create('', nx, ny, 1, gdal.GDT_Byte)

        # Set geotransform
        pixel_width = (extent.xMaximum() - extent.xMinimum()) / nx
        pixel_height = (extent.yMaximum() - extent.yMinimum()) / ny
        raster.SetGeoTransform((
            extent.xMinimum(), pixel_width, 0,
            extent.yMaximum(), 0, -pixel_height
        ))

        # Create in-memory OGR datasource with polygon
        mem_driver = ogr.GetDriverByName('Memory')
        mem_ds = mem_driver.CreateDataSource('')
        mem_layer = mem_ds.CreateLayer('mask', geom_type=ogr.wkbPolygon)

        # Create feature with polygon geometry
        feat_defn = mem_layer.GetLayerDefn()
        feat = ogr.Feature(feat_defn)

        # Convert QgsGeometry to OGR geometry
        wkt = polygon.asWkt()
        ogr_geom = ogr.CreateGeometryFromWkt(wkt)
        feat.SetGeometry(ogr_geom)
        mem_layer.CreateFeature(feat)

        # Rasterize: burn value 1 where polygon exists
        gdal.RasterizeLayer(raster, [1], mem_layer, burn_values=[1])

        # Read array and convert to boolean
        band = raster.GetRasterBand(1)
        mask_array = band.ReadAsArray()

        # Cleanup
        raster = None
        mem_ds = None

        return mask_array == 1

    def _rasterize_polygon_simple(self, polygon, shape, extent):
        """
        Simple fallback rasterization using point-in-polygon tests.

        Args:
            polygon: QgsGeometry polygon
            shape: Tuple (rows, cols) for output array
            extent: QgsRectangle of the grid extent

        Returns:
            Boolean numpy array
        """
        ny, nx = shape
        mask = np.zeros((ny, nx), dtype=bool)

        pixel_width = (extent.xMaximum() - extent.xMinimum()) / nx
        pixel_height = (extent.yMaximum() - extent.yMinimum()) / ny

        for iy in range(ny):
            for ix in range(nx):
                # Calculate cell center coordinates
                x = extent.xMinimum() + (ix + 0.5) * pixel_width
                y = extent.yMaximum() - (iy + 0.5) * pixel_height

                # Test if point is inside polygon
                point = QgsGeometry.fromPointXY(QgsPointXY(x, y))
                if polygon.contains(point):
                    mask[iy, ix] = True

        return mask

    def _classify_to_multipolygon(self, grid, extent, mask_polygon,
                                   classification_scheme, map_type='potential'):
        """
        Convert a classified raster grid to a multipolygon vector layer.

        Creates polygons for each classification level, clipped to the
        project boundary.

        Args:
            grid: 2D numpy array with values
            extent: QgsRectangle of the grid extent
            mask_polygon: QgsGeometry of project boundary for clipping
            classification_scheme: Dict mapping (min, max) to class info
            map_type: 'potential' or 'risk' for layer naming

        Returns:
            QgsVectorLayer with classified polygons
        """
        if not self.has_qgis:
            return None

        # Create memory layer
        crs_string = self.crs.authid() if self.crs else 'EPSG:4326'
        layer_name = f"GNA_{map_type.upper()}"
        layer = QgsVectorLayer(
            f'MultiPolygon?crs={crs_string}',
            layer_name,
            'memory'
        )

        provider = layer.dataProvider()

        # Add GNA-required fields
        fields = QgsFields()
        fields.append(QgsField('CLASSE', QVariant.String))
        fields.append(QgsField('LABEL', QVariant.String))
        fields.append(QgsField('VALORE_MIN', QVariant.Double))
        fields.append(QgsField('VALORE_MAX', QVariant.Double))
        fields.append(QgsField('COLORE', QVariant.String))
        fields.append(QgsField('AREA_MQ', QVariant.Double))
        provider.addAttributes(fields)
        layer.updateFields()

        ny, nx = grid.shape
        pixel_width = (extent.xMaximum() - extent.xMinimum()) / nx
        pixel_height = (extent.yMaximum() - extent.yMinimum()) / ny

        # Process each classification level
        for (min_val, max_val), class_info in classification_scheme.items():
            # Create mask for this class
            if max_val == 100:
                class_mask = (grid >= min_val) & (grid <= max_val) & ~np.isnan(grid)
            else:
                class_mask = (grid >= min_val) & (grid < max_val) & ~np.isnan(grid)

            if not np.any(class_mask):
                continue

            # Polygonize the class mask
            class_polygons = self._polygonize_mask(class_mask, extent, pixel_width, pixel_height)

            if not class_polygons:
                continue

            # Merge all polygons for this class into multipolygon
            merged_geom = None
            for poly_geom in class_polygons:
                if merged_geom is None:
                    merged_geom = poly_geom
                else:
                    merged_geom = merged_geom.combine(poly_geom)

            if merged_geom is None or merged_geom.isEmpty():
                continue

            # Clip to project boundary
            clipped = merged_geom.intersection(mask_polygon)

            if clipped.isEmpty():
                continue

            # Create feature
            feat = QgsFeature()
            feat.setGeometry(clipped)

            # Calculate area
            area = clipped.area()

            feat.setAttributes([
                class_info['code'],
                class_info['label'],
                float(min_val),
                float(max_val),
                class_info['color'],
                float(area)
            ])

            provider.addFeature(feat)

        layer.updateExtents()

        # Apply styling
        self._style_classified_layer(layer, map_type)

        return layer

    def _polygonize_mask(self, mask, extent, pixel_width, pixel_height):
        """
        Convert a boolean mask to polygon geometries.

        Uses a simple cell-based approach: each True cell becomes a polygon,
        then adjacent polygons are dissolved.

        Args:
            mask: 2D boolean numpy array
            extent: QgsRectangle
            pixel_width: Cell width
            pixel_height: Cell height

        Returns:
            List of QgsGeometry polygons
        """
        if not self.has_qgis:
            return []

        polygons = []
        ny, nx = mask.shape

        # Find connected regions using flood fill approach
        visited = np.zeros_like(mask, dtype=bool)

        def get_cell_polygon(iy, ix):
            """Create polygon for a single cell."""
            x0 = extent.xMinimum() + ix * pixel_width
            y0 = extent.yMaximum() - (iy + 1) * pixel_height
            x1 = x0 + pixel_width
            y1 = y0 + pixel_height

            return QgsGeometry.fromPolygonXY([[
                QgsPointXY(x0, y0),
                QgsPointXY(x1, y0),
                QgsPointXY(x1, y1),
                QgsPointXY(x0, y1),
                QgsPointXY(x0, y0)
            ]])

        # Create polygons for all True cells and dissolve
        cell_polys = []
        for iy in range(ny):
            for ix in range(nx):
                if mask[iy, ix]:
                    cell_polys.append(get_cell_polygon(iy, ix))

        if not cell_polys:
            return []

        # Merge all cell polygons
        merged = cell_polys[0]
        for poly in cell_polys[1:]:
            merged = merged.combine(poly)

        # Simplify to reduce vertex count
        tolerance = min(pixel_width, pixel_height) * 0.1
        simplified = merged.simplify(tolerance)

        if simplified and not simplified.isEmpty():
            return [simplified]
        elif merged and not merged.isEmpty():
            return [merged]

        return []

    def _style_classified_layer(self, layer, map_type='potential'):
        """
        Apply categorized styling to classified GNA layer.

        Args:
            layer: QgsVectorLayer with CLASSE and COLORE fields
            map_type: 'potential' or 'risk'
        """
        if not self.has_qgis:
            return

        try:
            from qgis.core import (
                QgsCategorizedSymbolRenderer,
                QgsRendererCategory,
                QgsFillSymbol
            )

            # Create categorized renderer based on CLASSE field
            renderer = QgsCategorizedSymbolRenderer('CLASSE')

            # Get unique classes from layer
            classes = set()
            for feat in layer.getFeatures():
                classe = feat['CLASSE']
                color = feat['COLORE']
                label = feat['LABEL']
                if classe:
                    classes.add((classe, color, label))

            # Create category for each class
            for classe, color, label in classes:
                symbol = QgsFillSymbol.createSimple({
                    'color': color,
                    'outline_color': '#333333',
                    'outline_width': '0.5'
                })

                category = QgsRendererCategory(classe, symbol, label)
                renderer.addCategory(category)

            layer.setRenderer(renderer)
            layer.triggerRepaint()

        except Exception as e:
            self.log_message(f"Error styling classified layer: {e}")

    def generate_gna_layers(self, ut_records, mask_polygon,
                           method='kde', cell_size=None,
                           vrp_scheme=None, vrd_scheme=None):
        """
        Generate complete GNA VRP and VRD layers from UT records.

        Convenience method that generates both potential and risk
        heatmaps masked to the project polygon.

        Args:
            ut_records: List of UT records with potential_score and risk_score
            mask_polygon: QgsGeometry of project boundary
            method: Interpolation method
            cell_size: Grid cell size
            vrp_scheme: VRP classification scheme (or use default)
            vrd_scheme: VRD classification scheme (or use default)

        Returns:
            Dictionary with vrp_layer, vrd_layer, vrp_raster, vrd_raster
        """
        from .ut_potential_calculator import UTPotentialCalculator

        # Extract points and scores from UT records
        potential_points = []
        potential_values = []
        risk_points = []
        risk_values = []

        for record in ut_records:
            # Get coordinates (need to be provided or extracted from geometry)
            x, y = None, None

            if hasattr(record, 'geometry') and record.geometry:
                centroid = record.geometry.centroid()
                x, y = centroid.x(), centroid.y()
            elif hasattr(record, 'coord_piane') and record.coord_piane:
                try:
                    coords = str(record.coord_piane).replace(' ', '').split(',')
                    x, y = float(coords[0]), float(coords[1])
                except:
                    pass

            # Fallback to coord_geografiche (lat, lon format)
            if x is None and hasattr(record, 'coord_geografiche') and record.coord_geografiche:
                try:
                    coords = str(record.coord_geografiche).replace(' ', '').split(',')
                    lat, lon = float(coords[0]), float(coords[1])
                    # For heatmap we use lon, lat order (x, y)
                    x, y = lon, lat
                except:
                    pass

            if x is None or y is None:
                continue

            # Get potential score
            potential = getattr(record, 'potential_score', None)
            if potential is not None:
                potential_points.append((x, y))
                potential_values.append(float(potential))

            # Get risk score
            risk = getattr(record, 'risk_score', None)
            if risk is not None:
                risk_points.append((x, y))
                risk_values.append(float(risk))

        result = {}

        # Generate VRP layer
        if potential_points and vrp_scheme:
            vrp_result = self.generate_masked_heatmap(
                potential_points, potential_values, mask_polygon,
                method=method, cell_size=cell_size,
                classification_scheme=vrp_scheme,
                map_type='potential'
            )
            result['vrp'] = vrp_result

        # Generate VRD layer
        if risk_points and vrd_scheme:
            vrd_result = self.generate_masked_heatmap(
                risk_points, risk_values, mask_polygon,
                method=method, cell_size=cell_size,
                classification_scheme=vrd_scheme,
                map_type='risk'
            )
            result['vrd'] = vrd_result

        return result
