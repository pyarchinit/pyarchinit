"""
Qt5/Qt6 Compatibility Layer for GeoArchaeo Plugin
Supports QGIS 3.x (Qt5) and QGIS 4.x (Qt6)
"""

from qgis.PyQt.QtCore import Qt, QVariant
from qgis.PyQt.QtWidgets import QAbstractItemView, QMessageBox, QDialogButtonBox, QFrame
from qgis.core import (
    Qgis, QgsWkbTypes, QgsVectorLayer, QgsMapLayerProxyModel, QgsFieldProxyModel,
    QgsColorRampShader, QgsProcessing, QgsProcessingParameterField, QgsProcessingParameterNumber
)

# Detect Qt version
try:
    from qgis.PyQt.QtCore import PYQT_VERSION_STR
    QT_VERSION = int(PYQT_VERSION_STR.split('.')[0])
except (ImportError, ValueError):
    QT_VERSION = 5


def enum_value(owner, scope, name):
    """
    Valore di un enum in modo compatibile Qt5/Qt6 e con tutte le versioni di QGIS:
    usa la forma scoped (owner.Scope.Name, obbligatoria in Qt6) quando esiste,
    altrimenti la forma storica (owner.Name) delle vecchie versioni PyQt5/QGIS.
    """
    scoped = getattr(owner, scope, None)
    if scoped is not None and hasattr(scoped, name):
        return getattr(scoped, name)
    return getattr(owner, name)


# Qt
Qt_UserRole = enum_value(Qt, 'ItemDataRole', 'UserRole')
Qt_RightDockWidgetArea = enum_value(Qt, 'DockWidgetArea', 'RightDockWidgetArea')
Qt_LeftDockWidgetArea = enum_value(Qt, 'DockWidgetArea', 'LeftDockWidgetArea')
Qt_AlignCenter = enum_value(Qt, 'AlignmentFlag', 'AlignCenter')
Qt_AlignTop = enum_value(Qt, 'AlignmentFlag', 'AlignTop')
Qt_SmoothTransformation = enum_value(Qt, 'TransformationMode', 'SmoothTransformation')
Qt_KeepAspectRatio = enum_value(Qt, 'AspectRatioMode', 'KeepAspectRatio')
Qt_RichText = enum_value(Qt, 'TextFormat', 'RichText')
Qt_ISODate = enum_value(Qt, 'DateFormat', 'ISODate')

# QVariant types (per QgsField)
QVariant_Int = enum_value(QVariant, 'Type', 'Int')
QVariant_Double = enum_value(QVariant, 'Type', 'Double')
QVariant_String = enum_value(QVariant, 'Type', 'String')

# Qgis
Qgis_Info = enum_value(Qgis, 'MessageLevel', 'Info')
Qgis_Warning = enum_value(Qgis, 'MessageLevel', 'Warning')
Qgis_Critical = enum_value(Qgis, 'MessageLevel', 'Critical')
Qgis_Success = enum_value(Qgis, 'MessageLevel', 'Success')
Qgis_Float32 = enum_value(Qgis, 'DataType', 'Float32')
QgsWkbTypes_Point = enum_value(QgsWkbTypes, 'Type', 'Point')

# Geometry type "Point" (QGIS >= 3.30: Qgis.GeometryType, prima QgsWkbTypes)
if hasattr(Qgis, 'GeometryType'):
    GeometryType_Point = enum_value(Qgis, 'GeometryType', 'Point')
else:
    GeometryType_Point = enum_value(QgsWkbTypes, 'GeometryType', 'PointGeometry')

# Widget
QListWidget_MultiSelection = enum_value(QAbstractItemView, 'SelectionMode', 'MultiSelection')
QFrame_NoFrame = enum_value(QFrame, 'Shape', 'NoFrame')
QMessageBox_Yes = enum_value(QMessageBox, 'StandardButton', 'Yes')
QMessageBox_No = enum_value(QMessageBox, 'StandardButton', 'No')
QDialogButtonBox_Ok = enum_value(QDialogButtonBox, 'StandardButton', 'Ok')
QDialogButtonBox_Cancel = enum_value(QDialogButtonBox, 'StandardButton', 'Cancel')
LayerFilter_Point = enum_value(QgsMapLayerProxyModel, 'Filter', 'PointLayer')
LayerFilter_Polygon = enum_value(QgsMapLayerProxyModel, 'Filter', 'PolygonLayer')
FieldFilter_Numeric = enum_value(QgsFieldProxyModel, 'Filter', 'Numeric')
ColorRamp_Interpolated = enum_value(QgsColorRampShader, 'Type', 'Interpolated')

# Processing
SourceType_VectorPoint = enum_value(QgsProcessing, 'SourceType', 'TypeVectorPoint')
SourceType_VectorPolygon = enum_value(QgsProcessing, 'SourceType', 'TypeVectorPolygon')
FieldType_Numeric = enum_value(QgsProcessingParameterField, 'DataType', 'Numeric')
NumberType_Double = enum_value(QgsProcessingParameterNumber, 'Type', 'Double')
NumberType_Integer = enum_value(QgsProcessingParameterNumber, 'Type', 'Integer')


def _call_first(obj, names, *args):
    """Chiama il primo metodo esistente tra `names` (nomi cambiati tra Qt5 e Qt6)."""
    for name in names:
        method = getattr(obj, name, None)
        if method is not None:
            return method(*args)
    raise AttributeError(f"{type(obj).__name__} has none of {names}")


def exec_dialog(dialog, *args):
    """Esegue un dialogo/menu: Qt6 ha rinominato il metodo (senza underscore finale)."""
    return _call_first(dialog, ('exec', 'exec' + '_'), *args)


def print_document(document, printer):
    """Stampa un QTextDocument (metodo rinominato in Qt6)."""
    return _call_first(document, ('print', 'print' + '_'), printer)


def pdf_printer(file_path):
    """QPrinter configurato per scrivere un PDF."""
    from qgis.PyQt.QtPrintSupport import QPrinter
    printer = QPrinter(enum_value(QPrinter, 'PrinterMode', 'HighResolution'))
    printer.setOutputFormat(enum_value(QPrinter, 'OutputFormat', 'PdfFormat'))
    printer.setOutputFileName(file_path)
    return printer


def question_yes_no(parent, title, text, default_no=True):
    """QMessageBox.question Qt5/Qt6 compatibile; True se l'utente conferma."""
    default = QMessageBox_No if default_no else QMessageBox_Yes
    reply = QMessageBox.question(parent, title, text, QMessageBox_Yes | QMessageBox_No, default)
    return reply == QMessageBox_Yes


def is_point_layer(layer):
    """True se il layer e' un vettoriale puntuale (Qt5/Qt6 safe)."""
    if not isinstance(layer, QgsVectorLayer):
        return False
    return layer.geometryType() == GeometryType_Point


def attribute_to_float(value):
    """
    Converte un attributo QGIS in float. Restituisce None per NULL/vuoto o
    valori non numerici (in PyQGIS un NULL arriva come QVariant, non come None).
    """
    if value is None:
        return None
    if isinstance(value, bool):
        return float(value)
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, QVariant):
        if value.isNull():
            return None
        value = value.value()
        if value is None:
            return None
    try:
        text = str(value).strip().replace(',', '.')
        if text == '' or text.upper() == 'NULL':
            return None
        return float(text)
    except (TypeError, ValueError):
        return None


def polygon_region(geometry):
    """
    Converte una QgsGeometry poligonale in un PolygonRegion del motore (anelli numpy),
    cosi' il campionamento puo' girare in un thread senza toccare oggetti QGIS.
    """
    from .core.geostat_engine import PolygonRegion
    if geometry is None or geometry.isEmpty():
        return None
    polygons = geometry.asMultiPolygon() if geometry.isMultipart() else [geometry.asPolygon()]
    converted = []
    for rings in polygons:
        if not rings:
            continue
        outer = [[pt.x(), pt.y()] for pt in rings[0]]
        holes = [[[pt.x(), pt.y()] for pt in ring] for ring in rings[1:]]
        converted.append((outer, holes))
    return PolygonRegion(converted) if converted else None
