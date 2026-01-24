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

try:
    import numpy as np
    # Test if numpy array API is working
    _ = np.array([1, 2, 3])
    NUMPY_AVAILABLE = True
except (ImportError, AttributeError):
    NUMPY_AVAILABLE = False

try:
    from scipy import stats
    from scipy.interpolate import griddata
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False

try:
    from osgeo import gdal, osr
    # Test if GDAL array support is working
    try:
        from osgeo import gdal_array
        GDAL_ARRAY_AVAILABLE = True
    except ImportError:
        GDAL_ARRAY_AVAILABLE = False
    GDAL_AVAILABLE = True
except ImportError:
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
