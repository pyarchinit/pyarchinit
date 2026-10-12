"""
Provider per QGIS Processing
Compatible with QGIS 3.x (Qt5) and QGIS 4.x (Qt6)
"""

import json
import os

import numpy as np

from qgis.core import (
    QgsProcessingProvider, QgsProcessingAlgorithm,
    QgsProcessingParameterVectorLayer, QgsProcessingParameterField,
    QgsProcessingParameterNumber, QgsProcessingParameterEnum,
    QgsProcessingParameterRasterDestination, QgsProcessingParameterExtent,
    QgsProcessingParameterFileDestination, QgsProcessingParameterBoolean,
    QgsProcessingParameterMultipleLayers, QgsProcessingParameterDateTime,
    QgsProcessingParameterFile, QgsProcessingParameterString,
    QgsProcessingParameterFeatureSink, QgsProcessingException,
    QgsProcessing, QgsRasterFileWriter, QgsApplication,
    QgsField, QgsFields, QgsFeature, QgsGeometry, QgsPointXY, QgsRectangle,
    QgsFeatureRequest, QgsCoordinateTransform
)
from qgis.PyQt.QtCore import QDateTime, QDate

from .compat import (
    QVariant_Int, QVariant_Double, QVariant_String, QgsWkbTypes_Point, Qt_ISODate,
    SourceType_VectorPoint, SourceType_VectorPolygon, FieldType_Numeric,
    NumberType_Double, NumberType_Integer, attribute_to_float, polygon_region
)
from .core.geostat_engine import to_native, VARIOGRAM_MODELS, limit_native_threads
from .i18n import tr2


# ----------------------------------------------------------------------
# Helpers comuni
# ----------------------------------------------------------------------
def _feature_point(feature):
    geom = feature.geometry()
    if geom is None or geom.isEmpty():
        return None
    if geom.isMultipart():
        try:
            return geom.asMultiPoint()[0]
        except Exception:
            return geom.centroid().asPoint()
    try:
        return geom.asPoint()
    except Exception:
        return geom.centroid().asPoint()


def _extract_points(layer, field=None):
    """Coordinate e valori numerici validi (NULL esclusi) di un layer di punti."""
    points, values = [], []
    request = QgsFeatureRequest()
    request.setSubsetOfAttributes([field], layer.fields()) if field else request.setSubsetOfAttributes([])
    for feature in layer.getFeatures(request):
        point = _feature_point(feature)
        if point is None:
            continue
        if field:
            value = attribute_to_float(feature[field])
            if value is None:
                continue
        else:
            value = 0.0
        points.append([point.x(), point.y()])
        values.append(value)
    return np.array(points, dtype=float).reshape(-1, 2), np.array(values, dtype=float)


def _write_raster(path, bands, x_grid, y_grid, crs, nodata=-9999.0):
    """
    Scrive uno o piu' array (ny, nx) con l'origine in basso a sinistra come
    raster georiferito (il primo pixel scritto e' quello in alto a sinistra).
    """
    from osgeo import gdal, osr
    bands = [np.asarray(b, dtype=float) for b in bands]
    ny, nx = bands[0].shape
    psx = float(x_grid[1] - x_grid[0]) if len(x_grid) > 1 else 1.0
    psy = float(y_grid[1] - y_grid[0]) if len(y_grid) > 1 else 1.0
    ext = os.path.splitext(path)[1][1:].lower()
    driver_name = QgsRasterFileWriter.driverForExtension(ext) or 'GTiff'
    driver = gdal.GetDriverByName(driver_name) or gdal.GetDriverByName('GTiff')
    options = ['COMPRESS=LZW'] if driver_name == 'GTiff' else []
    dataset = driver.Create(path, nx, ny, len(bands), gdal.GDT_Float32, options=options)
    if dataset is None:
        raise QgsProcessingException(f"Cannot create raster: {path}")
    dataset.SetGeoTransform([float(x_grid[0]) - psx / 2, psx, 0, float(y_grid[-1]) + psy / 2, 0, -psy])
    if crs is not None and crs.isValid():
        srs = osr.SpatialReference()
        srs.ImportFromWkt(crs.toWkt())
        dataset.SetProjection(srs.ExportToWkt())
    for i, band_data in enumerate(bands, start=1):
        band = dataset.GetRasterBand(i)
        band.WriteArray(np.flipud(np.where(np.isfinite(band_data), band_data, nodata)).astype(np.float32))
        band.SetNoDataValue(nodata)
        band.FlushCache()
    dataset = None
    return path


def _progress_callback(feedback):
    def progress(fraction):
        feedback.setProgress(int(fraction * 100))
        return not feedback.isCanceled()
    return progress


def _load_variogram(path):
    if not path or not os.path.exists(path):
        return None
    with open(path, 'r', encoding='utf-8') as handle:
        data = json.load(handle)
    return data if isinstance(data, dict) and data.get('model_params') else None


class _BaseAlgorithm(QgsProcessingAlgorithm):
    """Base con engine, gruppo e help."""
    GROUP = ('Geostatistica', 'Geostatistics')
    HELP = ('', '')

    def __init__(self, engine):
        super().__init__()
        self.engine = engine

    def createInstance(self):
        return type(self)(self.engine)

    def group(self):
        return tr2(*self.GROUP)

    def groupId(self):
        return self.GROUP[1].lower().replace(' ', '_')

    def shortHelpString(self):
        return tr2(*self.HELP)

    def processAlgorithm(self, parameters, context, feedback):
        # Processing esegue gli algoritmi in un thread secondario: limitiamo i
        # thread nativi di BLAS/OpenMP (vedi limit_native_threads).
        with limit_native_threads():
            return self._process(parameters, context, feedback)


class GeoArchaeoProvider(QgsProcessingProvider):
    """Provider Processing per GeoArchaeo"""

    def __init__(self, engine):
        super().__init__()
        self.engine = engine

    def loadAlgorithms(self):
        for alg in (VariogramAlgorithm, OrdinaryKrigingAlgorithm, CoKrigingAlgorithm,
                    SpatioTemporalKrigingAlgorithm, CompositionalAnalysisAlgorithm,
                    MLPatternRecognitionAlgorithm, OptimalSamplingAlgorithm, BatchKrigingAlgorithm):
            self.addAlgorithm(alg(self.engine))

    def id(self):
        return 'geoarchaeo'

    def name(self):
        return 'GeoArchaeo'

    def icon(self):
        return QgsApplication.getThemeIcon('/mActionShowStatisticalSummary.svg')


# ----------------------------------------------------------------------
# Variogramma
# ----------------------------------------------------------------------
class VariogramAlgorithm(_BaseAlgorithm):
    HELP = ('Calcola il variogramma sperimentale omnidirezionale e adatta il modello teorico '
            '(nugget, sill, range). Con "Calcola anisotropia" aggiunge i variogrammi direzionali '
            '(0°, 45°, 90°, 135°). Il file JSON prodotto puo\' essere passato a Ordinary Kriging.',
            'Computes the omnidirectional experimental variogram and fits the theoretical model '
            '(nugget, sill, range). With "Compute anisotropy" it adds the directional variograms '
            '(0°, 45°, 90°, 135°). The JSON output can be passed to Ordinary Kriging.')

    def name(self):
        return 'variogram'

    def displayName(self):
        return tr2('Analisi variogramma', 'Variogram analysis')

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterVectorLayer('INPUT', tr2('Layer punti', 'Point layer'),
                                                            [SourceType_VectorPoint]))
        self.addParameter(QgsProcessingParameterField('FIELD', tr2('Campo valore', 'Value field'),
                                                      parentLayerParameterName='INPUT',
                                                      type=FieldType_Numeric))
        self.addParameter(QgsProcessingParameterNumber('MAX_DISTANCE', tr2('Distanza massima (0 = automatica)',
                                                                           'Maximum distance (0 = automatic)'),
                                                       type=NumberType_Double, defaultValue=0.0,
                                                       minValue=0.0))
        self.addParameter(QgsProcessingParameterEnum('MODEL', tr2('Modello', 'Model'),
                                                     options=['Spherical', 'Exponential', 'Gaussian', 'Matérn'],
                                                     defaultValue=0))
        self.addParameter(QgsProcessingParameterNumber('N_LAGS', tr2('Numero di classi di distanza', 'Number of lags'),
                                                       type=NumberType_Integer, defaultValue=15,
                                                       minValue=3, maxValue=50))
        self.addParameter(QgsProcessingParameterBoolean('ANISOTROPY', tr2('Calcola anisotropia', 'Compute anisotropy'),
                                                        defaultValue=False))
        self.addParameter(QgsProcessingParameterFileDestination('OUTPUT', tr2('Variogramma (JSON)', 'Variogram (JSON)'),
                                                                'JSON files (*.json)'))

    def _process(self, parameters, context, feedback):
        layer = self.parameterAsVectorLayer(parameters, 'INPUT', context)
        field = self.parameterAsString(parameters, 'FIELD', context)
        max_dist = self.parameterAsDouble(parameters, 'MAX_DISTANCE', context)
        model_type = VARIOGRAM_MODELS[self.parameterAsEnum(parameters, 'MODEL', context)]
        n_lags = self.parameterAsInt(parameters, 'N_LAGS', context)
        check_aniso = self.parameterAsBool(parameters, 'ANISOTROPY', context)

        points, values = _extract_points(layer, field)
        if len(points) < 3:
            raise QgsProcessingException(tr2('Servono almeno 3 punti con valore numerico',
                                             'At least 3 points with a numeric value are required'))
        if max_dist <= 0:
            max_dist = self.engine.suggest_max_distance(points)
        feedback.pushInfo(f"Variogram: {len(points)} points, max distance {max_dist:.3g}, model {model_type}")

        result = self.engine.calculate_variogram(points, values, max_dist, model_type, check_aniso, n_lags=n_lags)
        result['layer'] = layer.name()
        result['field'] = field
        params = result['model_params']
        feedback.pushInfo(f"nugget={params['nugget']:.4g} sill={params['sill']:.4g} "
                          f"range={params['range']:.4g} rmse={params['rmse']:.4g}")
        if result.get('anisotropy'):
            feedback.pushInfo(f"anisotropy: {result['anisotropy']}")

        output_path = self.parameterAsFileOutput(parameters, 'OUTPUT', context)
        with open(output_path, 'w', encoding='utf-8') as handle:
            json.dump(to_native(result), handle, indent=2)
        return {'OUTPUT': output_path, 'NUGGET': params['nugget'], 'SILL': params['sill'], 'RANGE': params['range']}


# ----------------------------------------------------------------------
# Kriging
# ----------------------------------------------------------------------
class _KrigingOutputMixin:
    """Parametri/scrittura comuni degli output raster di kriging."""

    def _add_output_params(self):
        self.addParameter(QgsProcessingParameterRasterDestination('OUTPUT', tr2('Raster predizione', 'Prediction raster')))
        self.addParameter(QgsProcessingParameterRasterDestination(
            'OUTPUT_VARIANCE', tr2('Raster incertezza (dev. standard)', 'Uncertainty raster (std. deviation)'),
            optional=True, createByDefault=False))

    def _write_outputs(self, parameters, context, feedback, result, crs):
        outputs = {}
        output_path = self.parameterAsOutputLayer(parameters, 'OUTPUT', context)
        _write_raster(output_path, [result['predictions']], result['x_grid'], result['y_grid'], crs)
        outputs['OUTPUT'] = output_path
        var_path = self.parameterAsOutputLayer(parameters, 'OUTPUT_VARIANCE', context)
        if var_path and result.get('variances') is not None:
            std = np.sqrt(np.where(result['variances'] >= 0, result['variances'], np.nan))
            _write_raster(var_path, [std], result['x_grid'], result['y_grid'], crs)
            outputs['OUTPUT_VARIANCE'] = var_path
        if result.get('grid_capped'):
            feedback.pushWarning(tr2(f"Griglia limitata: risoluzione effettiva {result['pixel_size']:.4g}",
                                     f"Grid capped: effective cell size {result['pixel_size']:.4g}"))
        cv = result.get('cv_results')
        if cv:
            feedback.pushInfo(f"Cross-validation ({cv['n_valid']} pts): RMSE={cv['rmse']:.4g} MAE={cv['mae']:.4g} "
                              f"ME={cv['me']:.4g} R2={cv['r2']:.3f} MSDR={cv['msdr'] if cv['msdr'] is None else round(cv['msdr'], 3)}")
            outputs.update({'CV_RMSE': cv['rmse'], 'CV_MAE': cv['mae'], 'CV_R2': cv['r2']})
        return outputs


class OrdinaryKrigingAlgorithm(_BaseAlgorithm, _KrigingOutputMixin):
    HELP = ('Ordinary Kriging su griglia regolare con cross-validation leave-one-out. '
            'Se non viene fornito un variogramma (JSON dell\'algoritmo "Analisi variogramma") '
            'viene stimato automaticamente. La griglia e\' limitata a 500 celle per lato.',
            'Ordinary Kriging on a regular grid with leave-one-out cross-validation. '
            'If no variogram (JSON from the "Variogram analysis" algorithm) is given it is '
            'estimated automatically. The grid is limited to 500 cells per side.')

    def name(self):
        return 'ordinarykriging'

    def displayName(self):
        return 'Ordinary Kriging'

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterVectorLayer('INPUT', tr2('Layer punti', 'Point layer'),
                                                            [SourceType_VectorPoint]))
        self.addParameter(QgsProcessingParameterField('FIELD', tr2('Campo valore', 'Value field'),
                                                      parentLayerParameterName='INPUT',
                                                      type=FieldType_Numeric))
        self.addParameter(QgsProcessingParameterExtent('EXTENT', tr2('Estensione output', 'Output extent'), optional=True))
        self.addParameter(QgsProcessingParameterNumber('PIXEL_SIZE', tr2('Dimensione cella', 'Cell size'),
                                                       type=NumberType_Double, defaultValue=1.0,
                                                       minValue=1e-9))
        self.addParameter(QgsProcessingParameterFile('VARIOGRAM', tr2('File variogramma JSON (opzionale)',
                                                                      'Variogram JSON file (optional)'),
                                                     optional=True, extension='json'))
        self.addParameter(QgsProcessingParameterNumber('MAX_NEIGHBORS', tr2('Numero massimo di vicini', 'Maximum neighbours'),
                                                       type=NumberType_Integer, defaultValue=20,
                                                       minValue=3, maxValue=200))
        self._add_output_params()

    def _process(self, parameters, context, feedback):
        layer = self.parameterAsVectorLayer(parameters, 'INPUT', context)
        field = self.parameterAsString(parameters, 'FIELD', context)
        extent = self.parameterAsExtent(parameters, 'EXTENT', context, layer.crs())
        if extent is None or extent.isEmpty():
            extent = layer.extent()
        pixel_size = self.parameterAsDouble(parameters, 'PIXEL_SIZE', context)
        variogram = _load_variogram(self.parameterAsString(parameters, 'VARIOGRAM', context))
        max_neighbors = self.parameterAsInt(parameters, 'MAX_NEIGHBORS', context)

        points, values = _extract_points(layer, field)
        if len(points) < 3:
            raise QgsProcessingException(tr2('Servono almeno 3 punti con valore numerico',
                                             'At least 3 points with a numeric value are required'))
        feedback.pushInfo(f"Ordinary kriging: {len(points)} points")
        result = self.engine.ordinary_kriging(points, values, extent, pixel_size, variogram,
                                              max_neighbors=max_neighbors, progress=_progress_callback(feedback))
        return self._write_outputs(parameters, context, feedback, result, layer.crs())


class CoKrigingAlgorithm(_BaseAlgorithm, _KrigingOutputMixin):
    HELP = ('Co-kriging semplificato (regression kriging con covariate collocate): per ogni punto '
            'primario si prende il valore secondario piu\' vicino, si stima una regressione lineare '
            'primario ~ secondari e si esegue l\'ordinary kriging dei residui. Utile per fondere '
            'dati con densita\' diverse (es. GPR + magnetometria).',
            'Simplified co-kriging (regression kriging with collocated covariates): for every primary '
            'point the nearest secondary value is taken, a linear regression primary ~ secondaries is '
            'fitted and the residuals are interpolated with ordinary kriging. Useful to fuse data with '
            'different densities (e.g. GPR + magnetometry).')

    def name(self):
        return 'cokriging'

    def displayName(self):
        return tr2('Co-Kriging (regressione + kriging residui)', 'Co-Kriging (regression + residual kriging)')

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterVectorLayer('PRIMARY', tr2('Layer primario (es. GPR)', 'Primary layer (e.g. GPR)'),
                                                            [SourceType_VectorPoint]))
        self.addParameter(QgsProcessingParameterField('PRIMARY_FIELD', tr2('Campo primario', 'Primary field'),
                                                      parentLayerParameterName='PRIMARY',
                                                      type=FieldType_Numeric))
        self.addParameter(QgsProcessingParameterMultipleLayers('SECONDARY', tr2('Layer secondari (es. magnetometria)',
                                                                                'Secondary layers (e.g. magnetometry)'),
                                                               SourceType_VectorPoint))
        self.addParameter(QgsProcessingParameterString('SECONDARY_FIELDS',
                                                       tr2('Campi secondari separati da virgola (vuoto = primo campo numerico)',
                                                           'Secondary fields, comma separated (empty = first numeric field)'),
                                                       optional=True))
        self.addParameter(QgsProcessingParameterExtent('EXTENT', tr2('Estensione output', 'Output extent'), optional=True))
        self.addParameter(QgsProcessingParameterNumber('PIXEL_SIZE', tr2('Dimensione cella', 'Cell size'),
                                                       type=NumberType_Double, defaultValue=1.0,
                                                       minValue=1e-9))
        self._add_output_params()

    def _process(self, parameters, context, feedback):
        primary = self.parameterAsVectorLayer(parameters, 'PRIMARY', context)
        primary_field = self.parameterAsString(parameters, 'PRIMARY_FIELD', context)
        secondary_layers = self.parameterAsLayerList(parameters, 'SECONDARY', context)
        fields_text = self.parameterAsString(parameters, 'SECONDARY_FIELDS', context) or ''
        field_names = [f.strip() for f in fields_text.split(',') if f.strip()]
        extent = self.parameterAsExtent(parameters, 'EXTENT', context, primary.crs())
        if extent is None or extent.isEmpty():
            extent = primary.extent()
        pixel_size = self.parameterAsDouble(parameters, 'PIXEL_SIZE', context)

        pp, pv = _extract_points(primary, primary_field)
        secondary_data = []
        for i, layer in enumerate(secondary_layers):
            name = field_names[i] if i < len(field_names) else None
            if not name:
                numeric = [f.name() for f in layer.fields() if f.isNumeric()]
                if not numeric:
                    feedback.pushWarning(f"{layer.name()}: no numeric field, skipped")
                    continue
                name = numeric[0]
            sp, sv = _extract_points(layer, name)
            feedback.pushInfo(f"secondary {layer.name()}.{name}: {len(sp)} points")
            if len(sp):
                secondary_data.append((sp, sv))

        result = self.engine.co_kriging(pp, pv, secondary_data, extent, pixel_size,
                                        progress=_progress_callback(feedback))
        if result.get('regression'):
            reg = result['regression']
            feedback.pushInfo(f"regression R2={reg['r2']:.3f} coefficients={np.round(reg['coefficients'], 4).tolist()}")
        outputs = self._write_outputs(parameters, context, feedback, result, primary.crs())
        outputs['REGRESSION_R2'] = result['regression']['r2'] if result.get('regression') else None
        return outputs


class SpatioTemporalKrigingAlgorithm(_BaseAlgorithm, _KrigingOutputMixin):
    HELP = ('Kriging spazio-temporale: il tempo (giorni dal tempo target) viene trattato come terza '
            'dimensione scalata e si esegue l\'ordinary kriging 3D con variogramma esponenziale. '
            'Il campo temporale puo\' essere data/ora, testo ISO o numerico (anno).',
            'Spatio-temporal kriging: time (days from the target time) is treated as a scaled third '
            'dimension and a 3D ordinary kriging with exponential variogram is run. '
            'The time field can be date/time, ISO text or numeric (year).')

    def name(self):
        return 'spatiotemporal'

    def displayName(self):
        return tr2('Kriging spazio-temporale', 'Spatio-temporal kriging')

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterVectorLayer('INPUT', tr2('Layer con dati temporali', 'Layer with temporal data'),
                                                            [SourceType_VectorPoint]))
        self.addParameter(QgsProcessingParameterField('VALUE_FIELD', tr2('Campo valore', 'Value field'),
                                                      parentLayerParameterName='INPUT',
                                                      type=FieldType_Numeric))
        self.addParameter(QgsProcessingParameterField('TIME_FIELD', tr2('Campo temporale', 'Time field'),
                                                      parentLayerParameterName='INPUT'))
        self.addParameter(QgsProcessingParameterDateTime('TARGET_TIME', tr2('Tempo target', 'Target time')))
        self.addParameter(QgsProcessingParameterNumber('TIME_RANGE', tr2('Finestra temporale (giorni, 0 = tutti)',
                                                                         'Time window (days, 0 = all)'),
                                                       type=NumberType_Double, defaultValue=0.0,
                                                       minValue=0.0))
        self.addParameter(QgsProcessingParameterNumber('PIXEL_SIZE', tr2('Dimensione cella (0 = automatica)', 'Cell size (0 = automatic)'),
                                                       type=NumberType_Double, defaultValue=0.0,
                                                       minValue=0.0))
        self._add_output_params()

    @staticmethod
    def _days_from_target(value, target):
        if value is None:
            return None
        if isinstance(value, QDateTime):
            return target.secsTo(value) / 86400.0 if value.isValid() else None
        if isinstance(value, QDate):
            return float(target.date().daysTo(value)) if value.isValid() else None
        numeric = attribute_to_float(value)
        if numeric is not None:
            return (numeric - target.date().year()) * 365.25     # campo numerico = anno
        parsed = QDateTime.fromString(str(value), Qt_ISODate)
        if parsed.isValid():
            return target.secsTo(parsed) / 86400.0
        parsed = QDate.fromString(str(value), Qt_ISODate)
        if parsed.isValid():
            return float(target.date().daysTo(parsed))
        return None

    def _process(self, parameters, context, feedback):
        layer = self.parameterAsVectorLayer(parameters, 'INPUT', context)
        value_field = self.parameterAsString(parameters, 'VALUE_FIELD', context)
        time_field = self.parameterAsString(parameters, 'TIME_FIELD', context)
        target_time = self.parameterAsDateTime(parameters, 'TARGET_TIME', context)
        time_range = self.parameterAsDouble(parameters, 'TIME_RANGE', context)
        pixel_size = self.parameterAsDouble(parameters, 'PIXEL_SIZE', context)

        data = []
        skipped = 0
        for feature in layer.getFeatures():
            point = _feature_point(feature)
            value = attribute_to_float(feature[value_field])
            days = self._days_from_target(feature[time_field], target_time)
            if point is None or value is None or days is None:
                skipped += 1
                continue
            if time_range > 0 and abs(days) > time_range:
                continue
            data.append({'x': point.x(), 'y': point.y(), 't': days, 'value': value})
        if skipped:
            feedback.pushWarning(f"{skipped} features skipped (missing value/time)")
        if len(data) < 3:
            raise QgsProcessingException(tr2('Meno di 3 osservazioni valide nella finestra temporale',
                                             'Fewer than 3 valid observations in the time window'))
        feedback.pushInfo(f"Spatio-temporal kriging: {len(data)} observations")
        result = self.engine.spatiotemporal_kriging(
            data, target_time.toString(Qt_ISODate), layer.extent(),
            pixel_size=pixel_size if pixel_size > 0 else None, progress=_progress_callback(feedback))
        return self._write_outputs(parameters, context, feedback, result, layer.crs())


# ----------------------------------------------------------------------
# Composizionale
# ----------------------------------------------------------------------
class CompositionalAnalysisAlgorithm(_BaseAlgorithm):
    HELP = ('Trasformazione log-ratio (CLR / ILR / ALR) dei campi composizionali (es. sabbia, limo, '
            'argilla) e ordinary kriging di ogni componente trasformata: produce un raster multibanda '
            '(una banda per componente trasformata).',
            'Log-ratio transform (CLR / ILR / ALR) of the compositional fields (e.g. sand, silt, clay) '
            'and ordinary kriging of each transformed component: produces a multi-band raster '
            '(one band per transformed component).')

    def name(self):
        return 'compositional'

    def displayName(self):
        return tr2('Analisi composizionale del suolo', 'Soil compositional analysis')

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterVectorLayer('INPUT', tr2('Layer campioni', 'Samples layer'),
                                                            [SourceType_VectorPoint]))
        self.addParameter(QgsProcessingParameterField('COMP_FIELDS', tr2('Campi composizionali', 'Compositional fields'),
                                                      parentLayerParameterName='INPUT', allowMultiple=True,
                                                      type=FieldType_Numeric))
        self.addParameter(QgsProcessingParameterEnum('TRANSFORM', tr2('Trasformazione', 'Transform'),
                                                     options=['CLR (Centered Log-Ratio)', 'ILR (Isometric Log-Ratio)',
                                                              'ALR (Additive Log-Ratio)'], defaultValue=0))
        self.addParameter(QgsProcessingParameterNumber('PIXEL_SIZE', tr2('Dimensione cella (0 = automatica)', 'Cell size (0 = automatic)'),
                                                       type=NumberType_Double, defaultValue=0.0,
                                                       minValue=0.0))
        self.addParameter(QgsProcessingParameterRasterDestination('OUTPUT', tr2('Raster composizionale (multibanda)',
                                                                                'Compositional raster (multi-band)')))

    def _process(self, parameters, context, feedback):
        layer = self.parameterAsVectorLayer(parameters, 'INPUT', context)
        comp_fields = self.parameterAsFields(parameters, 'COMP_FIELDS', context)
        transform_type = ['clr', 'ilr', 'alr'][self.parameterAsEnum(parameters, 'TRANSFORM', context)]
        pixel_size = self.parameterAsDouble(parameters, 'PIXEL_SIZE', context)
        if len(comp_fields) < 2:
            raise QgsProcessingException(tr2('Servono almeno 2 campi composizionali', 'At least 2 compositional fields are required'))

        points, compositions = [], []
        for feature in layer.getFeatures():
            point = _feature_point(feature)
            values = [attribute_to_float(feature[f]) for f in comp_fields]
            if point is None or any(v is None for v in values):
                continue
            points.append([point.x(), point.y()])
            compositions.append(values)
        if len(points) < 3:
            raise QgsProcessingException(tr2('Meno di 3 campioni completi', 'Fewer than 3 complete samples'))

        result = self.engine.compositional_analysis(np.array(points), np.array(compositions), transform_type)
        transformed = result['transformed']
        extent = layer.extent()
        if pixel_size <= 0:
            pixel_size = self.engine.suggest_pixel_size(extent)
        bands, grids = [], None
        n_components = transformed.shape[1]
        for band in range(n_components):
            feedback.pushInfo(f"Kriging component {band + 1}/{n_components}")
            kr = self.engine.ordinary_kriging(np.array(points), transformed[:, band], extent, pixel_size,
                                              compute_cv=False)
            bands.append(kr['predictions'])
            grids = (kr['x_grid'], kr['y_grid'])
            feedback.setProgress(int(100 * (band + 1) / n_components))
            if feedback.isCanceled():
                break
        output_path = self.parameterAsOutputLayer(parameters, 'OUTPUT', context)
        _write_raster(output_path, bands, grids[0], grids[1], layer.crs())
        return {'OUTPUT': output_path}


# ----------------------------------------------------------------------
# Machine learning
# ----------------------------------------------------------------------
class MLPatternRecognitionAlgorithm(_BaseAlgorithm):
    GROUP = ('Machine Learning', 'Machine Learning')
    HELP = ('Raggruppa i punti (coordinate + attributi numerici) con K-Means, DBSCAN o Isolation Forest '
            '(anomalie), oppure classifica con Random Forest usando un campo etichetta: i punti con '
            'etichetta nota addestrano il modello, gli altri vengono classificati. '
            'L\'output e\' un layer di punti con l\'etichetta di ogni elemento.',
            'Groups the points (coordinates + numeric attributes) with K-Means, DBSCAN or Isolation Forest '
            '(anomalies), or classifies them with Random Forest using a label field: points with a known '
            'label train the model, the others are classified. '
            'The output is a point layer with the label of each feature.')

    METHODS = ['kmeans', 'dbscan', 'isolation_forest', 'random_forest']

    def name(self):
        return 'mlpattern'

    def displayName(self):
        return tr2('Pattern recognition ML', 'ML pattern recognition')

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterMultipleLayers('INPUTS', tr2('Layer di punti', 'Point layers'),
                                                               SourceType_VectorPoint))
        self.addParameter(QgsProcessingParameterEnum('ML_METHOD', tr2('Metodo', 'Method'),
                                                     options=['K-Means', 'DBSCAN', 'Isolation Forest (anomalies)',
                                                              'Random Forest (supervised)'], defaultValue=0))
        self.addParameter(QgsProcessingParameterNumber('N_CLUSTERS', tr2('Numero gruppi K-Means (0 = automatico)',
                                                                         'K-Means groups (0 = automatic)'),
                                                       type=NumberType_Integer, defaultValue=0,
                                                       minValue=0, maxValue=50))
        self.addParameter(QgsProcessingParameterString('LABEL_FIELD', tr2('Campo etichetta (solo Random Forest)',
                                                                          'Label field (Random Forest only)'),
                                                       optional=True))
        self.addParameter(QgsProcessingParameterFeatureSink('OUTPUT', tr2('Punti classificati', 'Classified points'),
                                                            SourceType_VectorPoint))

    def _process(self, parameters, context, feedback):
        layers = self.parameterAsLayerList(parameters, 'INPUTS', context)
        method = self.METHODS[self.parameterAsEnum(parameters, 'ML_METHOD', context)]
        n_clusters = self.parameterAsInt(parameters, 'N_CLUSTERS', context) or None
        label_field = (self.parameterAsString(parameters, 'LABEL_FIELD', context) or '').strip()
        if not layers:
            raise QgsProcessingException(tr2('Seleziona almeno un layer', 'Select at least one layer'))
        if method == 'random_forest' and not label_field:
            raise QgsProcessingException(tr2('Random Forest richiede un campo etichetta', 'Random Forest requires a label field'))

        layers_data, labels, sources = [], [], []
        for layer in layers:
            numeric = [f.name() for f in layer.fields() if f.isNumeric() and f.name() != label_field]
            data = {'name': layer.name(), 'points': [], 'features': []}
            has_label = label_field and layer.fields().indexOf(label_field) >= 0
            for feature in layer.getFeatures():
                point = _feature_point(feature)
                if point is None:
                    continue
                data['points'].append([point.x(), point.y()])
                data['features'].append([attribute_to_float(feature[n]) for n in numeric])
                sources.append(layer.name())
                if label_field:
                    raw = feature[label_field] if has_label else None
                    labels.append(None if raw is None or str(raw) == 'NULL' else raw)
            if data['points']:
                layers_data.append(data)
        feedback.pushInfo(f"ML {method}: {sum(len(d['points']) for d in layers_data)} points")
        result = self.engine.ml_pattern_recognition(layers_data, method, n_clusters=n_clusters,
                                                    labels=labels if label_field else None)

        fields = QgsFields()
        fields.append(QgsField('source_layer', QVariant_String))
        fields.append(QgsField('cluster_id', QVariant_Int))
        fields.append(QgsField('label', QVariant_String))
        sink, dest_id = self.parameterAsSink(parameters, 'OUTPUT', context, fields, QgsWkbTypes_Point, layers[0].crs())
        if sink is None:
            raise QgsProcessingException(self.invalidSinkError(parameters, 'OUTPUT'))
        class_names = result.get('class_names') or {}
        for (x, y), label, source in zip(result['coordinates'], result['labels'], sources):
            label = int(label)
            if method == 'isolation_forest':
                text = 'anomaly' if label == 1 else 'normal'
            elif method == 'dbscan' and label == -1:
                text = 'noise'
            else:
                text = str(class_names.get(label, f"group_{chr(ord('A') + label % 26)}"))
            feat = QgsFeature(fields)
            feat.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(float(x), float(y))))
            feat.setAttributes([source, label, text])
            sink.addFeature(feat)
        feedback.pushInfo(f"groups: {result['n_clusters']}  params: {result['params']}")
        return {'OUTPUT': dest_id, 'N_GROUPS': result['n_clusters']}


# ----------------------------------------------------------------------
# Batch kriging
# ----------------------------------------------------------------------
class BatchKrigingAlgorithm(_BaseAlgorithm, _KrigingOutputMixin):
    HELP = ('Ordinary kriging a tile per dataset grandi: il variogramma e\' stimato una volta su un '
            'sottocampione, ogni tile usa i punti nel tile piu\' un margine e le zone di sovrapposizione '
            'vengono mediate. La griglia puo\' arrivare a 3000 celle per lato.',
            'Tiled ordinary kriging for large datasets: the variogram is estimated once on a subsample, '
            'each tile uses the points inside the tile plus a margin and the overlap areas are averaged. '
            'The grid can reach 3000 cells per side.')

    def name(self):
        return 'batchkriging'

    def displayName(self):
        return tr2('Batch kriging (dataset grandi)', 'Batch kriging (large datasets)')

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterVectorLayer('INPUT', tr2('Layer punti', 'Point layer'),
                                                            [SourceType_VectorPoint]))
        self.addParameter(QgsProcessingParameterField('FIELD', tr2('Campo valore', 'Value field'),
                                                      parentLayerParameterName='INPUT',
                                                      type=FieldType_Numeric))
        self.addParameter(QgsProcessingParameterNumber('PIXEL_SIZE', tr2('Dimensione cella', 'Cell size'),
                                                       type=NumberType_Double, defaultValue=1.0,
                                                       minValue=1e-9))
        self.addParameter(QgsProcessingParameterNumber('TILE_SIZE', tr2('Dimensione tile', 'Tile size'),
                                                       type=NumberType_Double, defaultValue=100.0,
                                                       minValue=1e-9))
        self.addParameter(QgsProcessingParameterNumber('OVERLAP', tr2('Sovrapposizione tile (%)', 'Tile overlap (%)'),
                                                       type=NumberType_Double, defaultValue=10.0,
                                                       minValue=0, maxValue=50))
        self.addParameter(QgsProcessingParameterNumber('MAX_POINTS_PER_TILE', tr2('Max punti per tile', 'Max points per tile'),
                                                       type=NumberType_Integer, defaultValue=1000,
                                                       minValue=10))
        self._add_output_params()

    def _process(self, parameters, context, feedback):
        layer = self.parameterAsVectorLayer(parameters, 'INPUT', context)
        field = self.parameterAsString(parameters, 'FIELD', context)
        pixel_size = self.parameterAsDouble(parameters, 'PIXEL_SIZE', context)
        tile_size = self.parameterAsDouble(parameters, 'TILE_SIZE', context)
        overlap = self.parameterAsDouble(parameters, 'OVERLAP', context)
        max_points = self.parameterAsInt(parameters, 'MAX_POINTS_PER_TILE', context)

        points, values = _extract_points(layer, field)
        if len(points) < 3:
            raise QgsProcessingException(tr2('Servono almeno 3 punti con valore numerico',
                                             'At least 3 points with a numeric value are required'))
        feedback.pushInfo(f"Batch kriging: {len(points)} points, tile {tile_size}")
        result = self.engine.batch_kriging(points, values, layer.extent(), pixel_size, tile_size, overlap,
                                           max_points, progress=_progress_callback(feedback))
        feedback.pushInfo(f"{result['n_tiles']} tiles processed")
        return self._write_outputs(parameters, context, feedback, result, layer.crs())


# ----------------------------------------------------------------------
# Campionamento ottimale
# ----------------------------------------------------------------------
class OptimalSamplingAlgorithm(_BaseAlgorithm):
    GROUP = ('Campionamento', 'Sampling')
    HELP = ('Propone nuove posizioni di campionamento a partire dai punti esistenti: copertura maximin, '
            'riduzione della varianza di kriging, griglia stratificata o campionamento adattivo nelle '
            'zone meno dense. L\'area di studio (poligono) e\' opzionale.',
            'Proposes new sampling locations from the existing points: maximin coverage, kriging-variance '
            'reduction, stratified grid or adaptive sampling in sparser areas. The study area (polygon) is optional.')

    METHODS = ['maximin', 'variance', 'stratified', 'adaptive']

    def name(self):
        return 'optimalsampling'

    def displayName(self):
        return tr2('Nuovi punti di campionamento', 'New sampling locations')

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterVectorLayer('EXISTING', tr2('Punti esistenti', 'Existing points'),
                                                            [SourceType_VectorPoint]))
        self.addParameter(QgsProcessingParameterVectorLayer('BOUNDARY', tr2('Area di studio (opzionale)', 'Study area (optional)'),
                                                            [SourceType_VectorPolygon], optional=True))
        self.addParameter(QgsProcessingParameterNumber('N_NEW', tr2('Numero nuovi punti', 'Number of new points'),
                                                       type=NumberType_Integer, defaultValue=10,
                                                       minValue=1))
        self.addParameter(QgsProcessingParameterEnum('METHOD', tr2('Criterio', 'Criterion'),
                                                     options=['Maximin (coverage)', 'Kriging variance reduction',
                                                              'Stratified grid', 'Adaptive (sparser areas)'],
                                                     defaultValue=0))
        self.addParameter(QgsProcessingParameterFile('VARIOGRAM', tr2('File variogramma JSON (opzionale, per riduzione varianza)',
                                                                      'Variogram JSON file (optional, for variance reduction)'),
                                                     optional=True, extension='json'))
        self.addParameter(QgsProcessingParameterFeatureSink('OUTPUT', tr2('Punti proposti', 'Proposed points'),
                                                            SourceType_VectorPoint))

    def _process(self, parameters, context, feedback):
        existing_layer = self.parameterAsVectorLayer(parameters, 'EXISTING', context)
        boundary_layer = self.parameterAsVectorLayer(parameters, 'BOUNDARY', context)
        n_new = self.parameterAsInt(parameters, 'N_NEW', context)
        method = self.METHODS[self.parameterAsEnum(parameters, 'METHOD', context)]
        variogram = _load_variogram(self.parameterAsString(parameters, 'VARIOGRAM', context))

        existing_points, _ = _extract_points(existing_layer)
        boundary = None
        if boundary_layer is not None:
            geoms = [f.geometry() for f in boundary_layer.getFeatures()
                     if f.geometry() is not None and not f.geometry().isEmpty()]
            if geoms:
                boundary = QgsGeometry.unaryUnion(geoms) if len(geoms) > 1 else QgsGeometry(geoms[0])
                if boundary_layer.crs().isValid() and boundary_layer.crs() != existing_layer.crs():
                    boundary.transform(QgsCoordinateTransform(boundary_layer.crs(), existing_layer.crs(),
                                                              context.transformContext()))
                boundary = polygon_region(boundary)
        feedback.pushInfo(f"Sampling design: {n_new} new points, method {method}, {len(existing_points)} existing")
        new_points = self.engine.optimal_sampling_design(existing_points, boundary, n_new, method,
                                                         variogram_params=variogram)

        fields = QgsFields()
        fields.append(QgsField('id', QVariant_Int))
        fields.append(QgsField('type', QVariant_String))
        fields.append(QgsField('priority', QVariant_Double))
        sink, dest_id = self.parameterAsSink(parameters, 'OUTPUT', context, fields, QgsWkbTypes_Point,
                                             existing_layer.crs())
        if sink is None:
            raise QgsProcessingException(self.invalidSinkError(parameters, 'OUTPUT'))
        n = max(len(new_points), 1)
        for i, (x, y) in enumerate(new_points):
            feat = QgsFeature(fields)
            feat.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(float(x), float(y))))
            feat.setAttributes([i + 1, 'suggested', 1.0 - i / n])
            sink.addFeature(feat)
        return {'OUTPUT': dest_id, 'N_POINTS': int(len(new_points))}
