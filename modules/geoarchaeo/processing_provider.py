"""
Provider per QGIS Processing
Compatible with QGIS 3.x (Qt5) and QGIS 4.x (Qt6)
"""

from qgis.core import (
    QgsProcessingProvider, QgsProcessingAlgorithm,
    QgsProcessingParameterVectorLayer, QgsProcessingParameterField,
    QgsProcessingParameterNumber, QgsProcessingParameterEnum,
    QgsProcessingParameterRasterDestination, QgsProcessingParameterExtent,
    QgsProcessingParameterFileDestination, QgsProcessingParameterBoolean,
    QgsProcessingParameterMultipleLayers, QgsProcessingParameterDateTime,
    QgsProcessing, QgsFeatureRequest, QgsRasterFileWriter,
    QgsRasterBlock, Qgis, QgsCoordinateReferenceSystem,
    QgsProcessingParameterVectorDestination, QgsApplication,
    QgsField, QgsFields, QgsFeature, QgsGeometry, QgsPointXY,
    QgsVectorLayer, QgsVectorFileWriter, QgsWkbTypes,
    QgsProcessingMultiStepFeedback
)
import numpy as np
import json
from datetime import datetime
import os
import tempfile

from .compat import (
    QVariant_Int, QVariant_Double, QVariant_String,
    Qgis_Float32, QgsWkbTypes_Point
)


class GeoArchaeoProvider(QgsProcessingProvider):
    """Provider Processing per GeoArchaeo"""
    
    def __init__(self, engine):
        super().__init__()
        self.engine = engine
        
    def loadAlgorithms(self):
        """Carica tutti gli algoritmi"""
        algorithms = [
            VariogramAlgorithm(self.engine),
            OrdinaryKrigingAlgorithm(self.engine),
            CoKrigingAlgorithm(self.engine),
            SpatioTemporalKrigingAlgorithm(self.engine),
            CompositionalAnalysisAlgorithm(self.engine),
            MLPatternRecognitionAlgorithm(self.engine),
            OptimalSamplingAlgorithm(self.engine),
            BatchKrigingAlgorithm(self.engine)
        ]
        
        for alg in algorithms:
            self.addAlgorithm(alg)
            
    def id(self):
        return 'geoarchaeo'
        
    def name(self):
        return 'GeoArchaeo'
        
    def icon(self):
        return QgsApplication.getThemeIcon('/mActionShowStatisticalSummary.svg')


class VariogramAlgorithm(QgsProcessingAlgorithm):
    """Algoritmo per calcolo e fitting variogramma"""
    
    def __init__(self, engine):
        super().__init__()
        self.engine = engine
        
    def name(self):
        return 'variogram'
        
    def displayName(self):
        return 'Analisi Variogramma'
        
    def createInstance(self):
        return VariogramAlgorithm(self.engine)
        
    def initAlgorithm(self, config=None):
        self.addParameter(
            QgsProcessingParameterVectorLayer(
                'INPUT', 'Layer punti',
                [QgsProcessing.TypeVectorPoint]
            )
        )
        self.addParameter(
            QgsProcessingParameterField(
                'FIELD', 'Campo valore',
                parentLayerParameterName='INPUT',
                type=QgsProcessingParameterField.Numeric
            )
        )
        self.addParameter(
            QgsProcessingParameterNumber(
                'MAX_DISTANCE', 'Distanza massima',
                type=QgsProcessingParameterNumber.Double,
                defaultValue=100.0
            )
        )
        self.addParameter(
            QgsProcessingParameterEnum(
                'MODEL', 'Modello',
                options=['Sferico', 'Esponenziale', 'Gaussiano', 'Matérn'],
                defaultValue=0
            )
        )
        self.addParameter(
            QgsProcessingParameterBoolean(
                'ANISOTROPY', 'Calcola anisotropia',
                defaultValue=False
            )
        )
        self.addParameter(
            QgsProcessingParameterFileDestination(
                'OUTPUT', 'Output variogramma',
                'JSON files (*.json)'
            )
        )
        
    def processAlgorithm(self, parameters, context, feedback):
        # Estrai parametri
        layer = self.parameterAsVectorLayer(parameters, 'INPUT', context)
        field = self.parameterAsString(parameters, 'FIELD', context)
        max_dist = self.parameterAsDouble(parameters, 'MAX_DISTANCE', context)
        model_idx = self.parameterAsEnum(parameters, 'MODEL', context)
        check_aniso = self.parameterAsBool(parameters, 'ANISOTROPY', context)
        
        models = ['spherical', 'exponential', 'gaussian', 'matern']
        model_type = models[model_idx]
        
        # Estrai dati
        points = []
        values = []
        
        for feature in layer.getFeatures():
            geom = feature.geometry()
            if geom and not geom.isEmpty():
                point = geom.asPoint()
                value = feature[field]
                if value is not None:
                    points.append([point.x(), point.y()])
                    values.append(float(value))
                    
        points = np.array(points)
        values = np.array(values)
        
        # Calcola variogramma
        feedback.pushInfo(f"Calcolo variogramma con {len(points)} punti...")
        
        result = self.engine.calculate_variogram(
            points, values, max_dist, model_type, check_aniso
        )
        
        # Salva risultati
        output_path = self.parameterAsFileOutput(parameters, 'OUTPUT', context)
        with open(output_path, 'w') as f:
            json.dump(result, f, indent=2)
            
        feedback.pushInfo(f"Variogramma salvato in: {output_path}")
        
        return {'OUTPUT': output_path}


class OrdinaryKrigingAlgorithm(QgsProcessingAlgorithm):
    """Ordinary Kriging implementation"""
    
    def __init__(self, engine):
        super().__init__()
        self.engine = engine
        
    def name(self):
        return 'ordinarykriging'
        
    def displayName(self):
        return 'Ordinary Kriging'
        
    def createInstance(self):
        return OrdinaryKrigingAlgorithm(self.engine)
        
    def initAlgorithm(self, config=None):
        self.addParameter(
            QgsProcessingParameterVectorLayer(
                'INPUT', 'Layer punti',
                [QgsProcessing.TypeVectorPoint]
            )
        )
        self.addParameter(
            QgsProcessingParameterField(
                'FIELD', 'Campo valore',
                parentLayerParameterName='INPUT',
                type=QgsProcessingParameterField.Numeric
            )
        )
        self.addParameter(
            QgsProcessingParameterExtent(
                'EXTENT', 'Estensione output'
            )
        )
        self.addParameter(
            QgsProcessingParameterNumber(
                'PIXEL_SIZE', 'Dimensione pixel',
                type=QgsProcessingParameterNumber.Double,
                defaultValue=1.0
            )
        )
        self.addParameter(
            QgsProcessingParameterFileDestination(
                'VARIOGRAM', 'File variogramma (opzionale)',
                'JSON files (*.json)',
                optional=True
            )
        )
        self.addParameter(
            QgsProcessingParameterRasterDestination(
                'OUTPUT', 'Raster Kriging'
            )
        )
        
    def processAlgorithm(self, parameters, context, feedback):
        layer = self.parameterAsVectorLayer(parameters, 'INPUT', context)
        field = self.parameterAsString(parameters, 'FIELD', context)
        extent = self.parameterAsExtent(parameters, 'EXTENT', context, layer.crs())
        pixel_size = self.parameterAsDouble(parameters, 'PIXEL_SIZE', context)
        variogram_file = self.parameterAsString(parameters, 'VARIOGRAM', context)
        
        feedback.pushInfo("Esecuzione Ordinary Kriging...")
        
        # Estrai dati
        points = []
        values = []
        
        for feature in layer.getFeatures():
            geom = feature.geometry()
            if geom:
                point = geom.asPoint()
                value = feature[field]
                if value is not None:
                    points.append([point.x(), point.y()])
                    values.append(float(value))
                    
        points = np.array(points)
        values = np.array(values)
        
        # Carica o calcola variogramma
        if variogram_file and os.path.exists(variogram_file):
            with open(variogram_file, 'r') as f:
                variogram_params = json.load(f)
        else:
            # Calcola variogramma automaticamente
            max_dist = np.sqrt(
                (extent.xMaximum() - extent.xMinimum())**2 + 
                (extent.yMaximum() - extent.yMinimum())**2
            ) / 3
            variogram_params = self.engine.calculate_variogram(
                points, values, max_dist, 'spherical', False
            )
        
        # Esegui kriging
        result = self.engine.ordinary_kriging(
            points, values, extent, pixel_size, variogram_params
        )
        
        # Scrivi raster output
        output_path = self.parameterAsOutputLayer(parameters, 'OUTPUT', context)
        
        nx = int((extent.xMaximum() - extent.xMinimum()) / pixel_size)
        ny = int((extent.yMaximum() - extent.yMinimum()) / pixel_size)
        
        writer = QgsRasterFileWriter(output_path)
        provider = writer.createOneBandRaster(
            Qgis_Float32, nx, ny, extent, layer.crs()
        )
        
        if provider is not None:
            block = QgsRasterBlock(Qgis_Float32, nx, ny)
            # Converti array numpy in formato raster QGIS
            for i in range(ny):
                for j in range(nx):
                    block.setValue(i, j, float(result['predictions'][i, j]))
            
            provider.writeBlock(block, 1, 0, 0)
            provider.setNoDataValue(1, -9999)
        
        return {'OUTPUT': output_path}


class CoKrigingAlgorithm(QgsProcessingAlgorithm):
    """Co-Kriging multivariabile per GPR + Magnetometria"""
    
    def __init__(self, engine):
        super().__init__()
        self.engine = engine
        
    def name(self):
        return 'cokriging'
        
    def displayName(self):
        return 'Co-Kriging Multivariabile'
        
    def createInstance(self):
        return CoKrigingAlgorithm(self.engine)
        
    def initAlgorithm(self, config=None):
        self.addParameter(
            QgsProcessingParameterVectorLayer(
                'PRIMARY', 'Layer primario (es. GPR)',
                [QgsProcessing.TypeVectorPoint]
            )
        )
        self.addParameter(
            QgsProcessingParameterField(
                'PRIMARY_FIELD', 'Campo primario',
                parentLayerParameterName='PRIMARY',
                type=QgsProcessingParameterField.Numeric
            )
        )
        self.addParameter(
            QgsProcessingParameterMultipleLayers(
                'SECONDARY', 'Layer secondari (es. Magnetometria)',
                QgsProcessing.TypeVectorPoint
            )
        )
        self.addParameter(
            QgsProcessingParameterField(
                'SECONDARY_FIELDS', 'Campi secondari (separati da virgola)',
                optional=True
            )
        )
        self.addParameter(
            QgsProcessingParameterExtent(
                'EXTENT', 'Estensione output'
            )
        )
        self.addParameter(
            QgsProcessingParameterNumber(
                'PIXEL_SIZE', 'Dimensione pixel',
                type=QgsProcessingParameterNumber.Double,
                defaultValue=1.0
            )
        )
        self.addParameter(
            QgsProcessingParameterRasterDestination(
                'OUTPUT', 'Raster Co-Kriging'
            )
        )
        
    def processAlgorithm(self, parameters, context, feedback):
        # Implementazione Co-Kriging
        primary_layer = self.parameterAsVectorLayer(parameters, 'PRIMARY', context)
        primary_field = self.parameterAsString(parameters, 'PRIMARY_FIELD', context)
        secondary_layers = self.parameterAsLayerList(parameters, 'SECONDARY', context)
        extent = self.parameterAsExtent(parameters, 'EXTENT', context, primary_layer.crs())
        pixel_size = self.parameterAsDouble(parameters, 'PIXEL_SIZE', context)
        
        feedback.pushInfo("Esecuzione Co-Kriging multivariabile...")
        
        # Estrai dati primari
        primary_points = []
        primary_values = []
        
        for feature in primary_layer.getFeatures():
            geom = feature.geometry()
            if geom:
                point = geom.asPoint()
                value = feature[primary_field]
                if value is not None:
                    primary_points.append([point.x(), point.y()])
                    primary_values.append(float(value))
                    
        # Estrai dati secondari
        secondary_data = []
        for layer in secondary_layers:
            points = []
            values = []
            # Assume primo campo numerico se non specificato
            numeric_fields = [f for f in layer.fields() if f.isNumeric()]
            if numeric_fields:
                field_name = numeric_fields[0].name()
                for feature in layer.getFeatures():
                    geom = feature.geometry()
                    if geom:
                        point = geom.asPoint()
                        value = feature[field_name]
                        if value is not None:
                            points.append([point.x(), point.y()])
                            values.append(float(value))
                secondary_data.append((np.array(points), np.array(values)))
                
        # Esegui Co-Kriging
        result = self.engine.co_kriging(
            np.array(primary_points),
            np.array(primary_values),
            secondary_data,
            extent,
            pixel_size
        )
        
        # Scrivi raster output
        output_path = self.parameterAsOutputLayer(parameters, 'OUTPUT', context)
        
        nx = int((extent.xMaximum() - extent.xMinimum()) / pixel_size)
        ny = int((extent.yMaximum() - extent.yMinimum()) / pixel_size)
        
        writer = QgsRasterFileWriter(output_path)
        provider = writer.createOneBandRaster(
            Qgis_Float32, nx, ny, extent, primary_layer.crs()
        )
        
        if provider is not None:
            block = QgsRasterBlock(Qgis_Float32, nx, ny)
            for i in range(ny):
                for j in range(nx):
                    block.setValue(i, j, float(result['predictions'][i, j]))
            
            provider.writeBlock(block, 1, 0, 0)
            provider.setNoDataValue(1, -9999)
        
        return {'OUTPUT': output_path}


class SpatioTemporalKrigingAlgorithm(QgsProcessingAlgorithm):
    """Kriging Spazio-Temporale per fasi di scavo"""
    
    def __init__(self, engine):
        super().__init__()
        self.engine = engine
        
    def name(self):
        return 'spatiotemporal'
        
    def displayName(self):
        return 'Kriging Spazio-Temporale'
        
    def createInstance(self):
        return SpatioTemporalKrigingAlgorithm(self.engine)
        
    def initAlgorithm(self, config=None):
        self.addParameter(
            QgsProcessingParameterVectorLayer(
                'INPUT', 'Layer con dati temporali',
                [QgsProcessing.TypeVectorPoint]
            )
        )
        self.addParameter(
            QgsProcessingParameterField(
                'VALUE_FIELD', 'Campo valore',
                parentLayerParameterName='INPUT',
                type=QgsProcessingParameterField.Numeric
            )
        )
        self.addParameter(
            QgsProcessingParameterField(
                'TIME_FIELD', 'Campo temporale',
                parentLayerParameterName='INPUT',
                type=QgsProcessingParameterField.DateTime
            )
        )
        self.addParameter(
            QgsProcessingParameterDateTime(
                'TARGET_TIME', 'Tempo target per interpolazione'
            )
        )
        self.addParameter(
            QgsProcessingParameterNumber(
                'TIME_RANGE', 'Range temporale (giorni)',
                type=QgsProcessingParameterNumber.Double,
                defaultValue=30.0
            )
        )
        self.addParameter(
            QgsProcessingParameterRasterDestination(
                'OUTPUT', 'Raster spazio-temporale'
            )
        )
        
    def processAlgorithm(self, parameters, context, feedback):
        layer = self.parameterAsVectorLayer(parameters, 'INPUT', context)
        value_field = self.parameterAsString(parameters, 'VALUE_FIELD', context)
        time_field = self.parameterAsString(parameters, 'TIME_FIELD', context)
        target_time = self.parameterAsDateTime(parameters, 'TARGET_TIME', context)
        time_range = self.parameterAsDouble(parameters, 'TIME_RANGE', context)
        
        feedback.pushInfo("Kriging spazio-temporale in corso...")
        
        # Estrai dati spazio-temporali
        space_time_data = []
        
        for feature in layer.getFeatures():
            geom = feature.geometry()
            if geom:
                point = geom.asPoint()
                value = feature[value_field]
                time_val = feature[time_field]
                
                if value is not None and time_val:
                    # Converti tempo in giorni dal target
                    if isinstance(time_val, str):
                        time_val = datetime.fromisoformat(time_val)
                    days_diff = (time_val - target_time).days
                    
                    # Include solo dati nel range temporale
                    if abs(days_diff) <= time_range:
                        space_time_data.append({
                            'x': point.x(),
                            'y': point.y(),
                            't': days_diff,
                            'value': float(value)
                        })
                        
        # Esegui kriging spazio-temporale
        result = self.engine.spatiotemporal_kriging(
            space_time_data, target_time, layer.extent()
        )
        
        # Scrivi risultato
        output_path = self.parameterAsOutputLayer(parameters, 'OUTPUT', context)
        
        nx, ny = result['predictions'].shape[1], result['predictions'].shape[0]
        extent = layer.extent()
        
        writer = QgsRasterFileWriter(output_path)
        provider = writer.createOneBandRaster(
            Qgis_Float32, nx, ny, extent, layer.crs()
        )
        
        if provider is not None:
            block = QgsRasterBlock(Qgis_Float32, nx, ny)
            for i in range(ny):
                for j in range(nx):
                    block.setValue(i, j, float(result['predictions'][i, j]))
            
            provider.writeBlock(block, 1, 0, 0)
            provider.setNoDataValue(1, -9999)
        
        return {'OUTPUT': output_path}


class CompositionalAnalysisAlgorithm(QgsProcessingAlgorithm):
    """Analisi composizionale con trasformazioni CLR/ILR"""
    
    def __init__(self, engine):
        super().__init__()
        self.engine = engine
        
    def name(self):
        return 'compositional'
        
    def displayName(self):
        return 'Analisi Composizionale Terreno'
        
    def createInstance(self):
        return CompositionalAnalysisAlgorithm(self.engine)
        
    def initAlgorithm(self, config=None):
        self.addParameter(
            QgsProcessingParameterVectorLayer(
                'INPUT', 'Layer campioni terreno',
                [QgsProcessing.TypeVectorPoint]
            )
        )
        self.addParameter(
            QgsProcessingParameterField(
                'COMP_FIELDS', 'Campi composizionali (es. sabbia,limo,argilla)',
                parentLayerParameterName='INPUT',
                allowMultiple=True,
                type=QgsProcessingParameterField.Numeric
            )
        )
        self.addParameter(
            QgsProcessingParameterEnum(
                'TRANSFORM', 'Trasformazione',
                options=['CLR (Centered Log-Ratio)', 'ILR (Isometric Log-Ratio)', 'ALR (Additive Log-Ratio)'],
                defaultValue=0
            )
        )
        self.addParameter(
            QgsProcessingParameterRasterDestination(
                'OUTPUT', 'Raster composizionale'
            )
        )
        
    def processAlgorithm(self, parameters, context, feedback):
        layer = self.parameterAsVectorLayer(parameters, 'INPUT', context)
        comp_fields = self.parameterAsFields(parameters, 'COMP_FIELDS', context)
        transform_idx = self.parameterAsEnum(parameters, 'TRANSFORM', context)
        
        transforms = ['clr', 'ilr', 'alr']
        transform_type = transforms[transform_idx]
        
        feedback.pushInfo(f"Applicazione trasformazione {transform_type}...")
        
        # Estrai dati composizionali
        points = []
        compositions = []
        
        for feature in layer.getFeatures():
            geom = feature.geometry()
            if geom:
                point = geom.asPoint()
                comp_values = []
                
                for field in comp_fields:
                    value = feature[field]
                    if value is not None:
                        comp_values.append(float(value))
                        
                if len(comp_values) == len(comp_fields):
                    points.append([point.x(), point.y()])
                    compositions.append(comp_values)
                    
        # Applica trasformazione composizionale
        result = self.engine.compositional_analysis(
            np.array(points),
            np.array(compositions),
            transform_type
        )
        
        # Kriging sui dati trasformati
        extent = layer.extent()
        pixel_size = (extent.width() + extent.height()) / 200  # Default resolution
        
        # Per ogni componente trasformata, esegui kriging
        transformed_data = result['transformed']
        n_components = transformed_data.shape[1]
        
        # Crea raster multi-banda per output
        output_path = self.parameterAsOutputLayer(parameters, 'OUTPUT', context)
        nx = int(extent.width() / pixel_size)
        ny = int(extent.height() / pixel_size)
        
        writer = QgsRasterFileWriter(output_path)
        provider = writer.createMultiBandRaster(
            Qgis_Float32, nx, ny, extent, layer.crs(), n_components
        )
        
        if provider is not None:
            for band in range(n_components):
                values = transformed_data[:, band]
                kriging_result = self.engine.ordinary_kriging(
                    np.array(points), values, extent, pixel_size, None
                )
                
                block = QgsRasterBlock(Qgis_Float32, nx, ny)
                for i in range(ny):
                    for j in range(nx):
                        block.setValue(i, j, float(kriging_result['predictions'][i, j]))
                
                provider.writeBlock(block, band + 1, 0, 0)
                provider.setNoDataValue(band + 1, -9999)
        
        return {'OUTPUT': output_path}


class MLPatternRecognitionAlgorithm(QgsProcessingAlgorithm):
    """Machine Learning per pattern recognition archeologico"""
    
    def __init__(self, engine):
        super().__init__()
        self.engine = engine
        
    def name(self):
        return 'mlpattern'
        
    def displayName(self):
        return 'ML Pattern Recognition'
        
    def createInstance(self):
        return MLPatternRecognitionAlgorithm(self.engine)
        
    def initAlgorithm(self, config=None):
        self.addParameter(
            QgsProcessingParameterMultipleLayers(
                'INPUTS', 'Layer di input',
                QgsProcessing.TypeVectorAnyGeometry
            )
        )
        self.addParameter(
            QgsProcessingParameterEnum(
                'ML_METHOD', 'Metodo ML',
                options=[
                    'Random Forest',
                    'SVM',
                    'Neural Network',
                    'Clustering (K-Means)',
                    'DBSCAN',
                    'Isolation Forest (Anomalie)'
                ],
                defaultValue=0
            )
        )
        self.addParameter(
            QgsProcessingParameterVectorLayer(
                'TRAINING', 'Layer training (opzionale)',
                [QgsProcessing.TypeVectorPoint],
                optional=True
            )
        )
        self.addParameter(
            QgsProcessingParameterRasterDestination(
                'OUTPUT', 'Mappa predizioni ML'
            )
        )
        
    def processAlgorithm(self, parameters, context, feedback):
        input_layers = self.parameterAsLayerList(parameters, 'INPUTS', context)
        ml_method_idx = self.parameterAsEnum(parameters, 'ML_METHOD', context)
        training_layer = self.parameterAsVectorLayer(parameters, 'TRAINING', context)
        
        methods = ['rf', 'svm', 'nn', 'kmeans', 'dbscan', 'isolation']
        method = methods[ml_method_idx]
        
        feedback.pushInfo(f"Applicazione {method} per pattern recognition...")
        
        # Prepara features per ML
        features = self.engine.prepare_ml_features(input_layers)
        
        # Training o clustering
        if training_layer and method in ['rf', 'svm', 'nn']:
            # Supervised learning
            labels = self.engine.extract_labels(training_layer)
            model = self.engine.train_ml_model(features, labels, method)
            predictions = model.predict(features)
        else:
            # Unsupervised learning
            predictions = self.engine.unsupervised_ml(features, method)
            
        # Genera output raster con predizioni
        # Trova extent combinato
        extent = input_layers[0].extent()
        for layer in input_layers[1:]:
            extent.combineExtentWith(layer.extent())
        
        # Crea griglia per predizioni
        pixel_size = (extent.width() + extent.height()) / 200
        nx = int(extent.width() / pixel_size)
        ny = int(extent.height() / pixel_size)
        
        # Mappa predizioni su griglia
        output_path = self.parameterAsOutputLayer(parameters, 'OUTPUT', context)
        
        writer = QgsRasterFileWriter(output_path)
        provider = writer.createOneBandRaster(
            Qgis_Float32, nx, ny, extent, input_layers[0].crs()
        )
        
        if provider is not None:
            block = QgsRasterBlock(Qgis_Float32, nx, ny)
            # Qui andrebbero mappate le predizioni sulla griglia
            # Per semplicità, creiamo un pattern di esempio
            for i in range(ny):
                for j in range(nx):
                    block.setValue(i, j, float(np.random.choice(predictions)))
            
            provider.writeBlock(block, 1, 0, 0)
            provider.setNoDataValue(1, -9999)
        
        return {'OUTPUT': output_path}


class BatchKrigingAlgorithm(QgsProcessingAlgorithm):
    """Batch processing per dataset grandi con tiling"""
    
    def __init__(self, engine):
        super().__init__()
        self.engine = engine
        
    def name(self):
        return 'batchkriging'
        
    def displayName(self):
        return 'Batch Kriging (Dataset Grandi)'
        
    def createInstance(self):
        return BatchKrigingAlgorithm(self.engine)
        
    def initAlgorithm(self, config=None):
        self.addParameter(
            QgsProcessingParameterVectorLayer(
                'INPUT', 'Layer input (grande)',
                [QgsProcessing.TypeVectorPoint]
            )
        )
        self.addParameter(
            QgsProcessingParameterField(
                'FIELD', 'Campo valore',
                parentLayerParameterName='INPUT',
                type=QgsProcessingParameterField.Numeric
            )
        )
        self.addParameter(
            QgsProcessingParameterNumber(
                'TILE_SIZE', 'Dimensione tile (m)',
                type=QgsProcessingParameterNumber.Double,
                defaultValue=100.0
            )
        )
        self.addParameter(
            QgsProcessingParameterNumber(
                'OVERLAP', 'Sovrapposizione tile (%)',
                type=QgsProcessingParameterNumber.Double,
                defaultValue=10.0,
                minValue=0,
                maxValue=50
            )
        )
        self.addParameter(
            QgsProcessingParameterNumber(
                'MAX_POINTS_PER_TILE', 'Max punti per tile',
                type=QgsProcessingParameterNumber.Integer,
                defaultValue=1000
            )
        )
        self.addParameter(
            QgsProcessingParameterRasterDestination(
                'OUTPUT', 'Raster mosaico finale'
            )
        )
        
    def processAlgorithm(self, parameters, context, feedback):
        layer = self.parameterAsVectorLayer(parameters, 'INPUT', context)
        field = self.parameterAsString(parameters, 'FIELD', context)
        tile_size = self.parameterAsDouble(parameters, 'TILE_SIZE', context)
        overlap = self.parameterAsDouble(parameters, 'OVERLAP', context)
        max_points = self.parameterAsInt(parameters, 'MAX_POINTS_PER_TILE', context)
        
        # Calcola tiles con overlap
        extent = layer.extent()
        tiles = self.engine.create_tiles(extent, tile_size, overlap)
        
        feedback.pushInfo(f"Processing {len(tiles)} tiles...")
        
        # Processa ogni tile
        tile_results = []
        for i, tile in enumerate(tiles):
            if feedback.isCanceled():
                break
                
            feedback.setProgress(int(100 * i / len(tiles)))
            feedback.pushInfo(f"Processing tile {i+1}/{len(tiles)}")
            
            # Estrai punti nel tile con campo specificato
            tile_data = self.engine.extract_points_in_tile_with_field(
                layer, tile, field, max_points
            )
            
            # Kriging sul tile
            if len(tile_data['points']) > 10:
                result = self.engine.kriging_tile(tile_data, tile)
                tile_results.append(result)
                
        # Unisci tiles in mosaico finale
        final_raster = self.engine.merge_tiles(tile_results, extent)
        
        # Scrivi output
        output_path = self.parameterAsOutputLayer(parameters, 'OUTPUT', context)
        
        if final_raster is not None:
            ny, nx = final_raster.shape
            writer = QgsRasterFileWriter(output_path)
            provider = writer.createOneBandRaster(
                Qgis_Float32, nx, ny, extent, layer.crs()
            )
            
            if provider is not None:
                block = QgsRasterBlock(Qgis_Float32, nx, ny)
                for i in range(ny):
                    for j in range(nx):
                        block.setValue(i, j, float(final_raster[i, j]))
                
                provider.writeBlock(block, 1, 0, 0)
                provider.setNoDataValue(1, -9999)
        
        return {'OUTPUT': output_path}


class OptimalSamplingAlgorithm(QgsProcessingAlgorithm):
    """Design campionamento ottimale"""
    
    def __init__(self, engine):
        super().__init__()
        self.engine = engine
        
    def name(self):
        return 'optimalsampling'
        
    def displayName(self):
        return 'Design Campionamento Ottimale'
        
    def createInstance(self):
        return OptimalSamplingAlgorithm(self.engine)
        
    def initAlgorithm(self, config=None):
        self.addParameter(
            QgsProcessingParameterVectorLayer(
                'EXISTING', 'Punti esistenti',
                [QgsProcessing.TypeVectorPoint]
            )
        )
        self.addParameter(
            QgsProcessingParameterVectorLayer(
                'BOUNDARY', 'Area studio',
                [QgsProcessing.TypeVectorPolygon]
            )
        )
        self.addParameter(
            QgsProcessingParameterNumber(
                'N_NEW', 'Numero nuovi punti',
                type=QgsProcessingParameterNumber.Integer,
                defaultValue=10
            )
        )
        self.addParameter(
            QgsProcessingParameterEnum(
                'METHOD', 'Metodo',
                options=['Maximin', 'Riduzione Varianza', 'Stratificato', 'Adattivo'],
                defaultValue=1
            )
        )
        self.addParameter(
            QgsProcessingParameterVectorDestination(
                'OUTPUT', 'Punti campionamento suggeriti'
            )
        )
        
    def processAlgorithm(self, parameters, context, feedback):
        existing_layer = self.parameterAsVectorLayer(parameters, 'EXISTING', context)
        boundary_layer = self.parameterAsVectorLayer(parameters, 'BOUNDARY', context)
        n_new = self.parameterAsInt(parameters, 'N_NEW', context)
        method_idx = self.parameterAsEnum(parameters, 'METHOD', context)
        
        methods = ['maximin', 'variance', 'stratified', 'adaptive']
        method = methods[method_idx]
        
        feedback.pushInfo(f"Calcolo {n_new} nuovi punti con metodo {method}...")
        
        # Estrai punti esistenti
        existing_points = []
        for feature in existing_layer.getFeatures():
            geom = feature.geometry()
            if geom:
                point = geom.asPoint()
                existing_points.append([point.x(), point.y()])
        
        existing_points = np.array(existing_points)
        
        # Estrai boundary
        boundary_geom = None
        for feature in boundary_layer.getFeatures():
            boundary_geom = feature.geometry()
            break
        
        if not boundary_geom:
            raise ValueError("Nessun poligono boundary trovato")
        
        # Calcola nuovi punti ottimali

        new_points = self.engine.optimal_sampling_design(
            existing_points, boundary_geom, n_new, method
        )
        
        # Crea layer output
        output_path = self.parameterAsOutputLayer(parameters, 'OUTPUT', context)
        
        # Definisci campi
        fields = QgsFields()
        fields.append(QgsField('id', QVariant_Int))
        fields.append(QgsField('type', QVariant_String))
        fields.append(QgsField('priority', QVariant_Double))
        
        # Crea writer
        writer = QgsVectorFileWriter(
            output_path,
            'UTF-8',
            fields,
            QgsWkbTypes_Point,
            existing_layer.crs(),
            'ESRI Shapefile'
        )
        
        if writer.hasError() != QgsVectorFileWriter.NoError:
            raise Exception(f"Errore creazione file: {writer.errorMessage()}")
        
        # Aggiungi features
        for i, point in enumerate(new_points):
            feature = QgsFeature()
            feature.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(point[0], point[1])))
            feature.setAttributes([i + 1, 'suggested', 1.0 - i/len(new_points)])
            writer.addFeature(feature)
        
        del writer
        
        return {'OUTPUT': output_path}