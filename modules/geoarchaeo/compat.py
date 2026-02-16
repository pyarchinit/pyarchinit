"""
Qt5/Qt6 Compatibility Layer for GeoArchaeo Plugin
Supports QGIS 3.x (Qt5) and QGIS 4.x (Qt6)
"""

from qgis.PyQt.QtCore import Qt, QVariant
from qgis.core import Qgis, QgsWkbTypes

# Detect Qt version
try:
    from qgis.PyQt.QtCore import PYQT_VERSION_STR
    QT_VERSION = int(PYQT_VERSION_STR.split('.')[0])
except:
    QT_VERSION = 5

# Qt enums compatibility
if QT_VERSION >= 6:
    # Qt6 style - fully qualified enums
    Qt_UserRole = Qt.ItemDataRole.UserRole
    Qt_RightDockWidgetArea = Qt.DockWidgetArea.RightDockWidgetArea
    Qt_LeftDockWidgetArea = Qt.DockWidgetArea.LeftDockWidgetArea

    # QVariant types
    QVariant_Int = QVariant.Type.Int
    QVariant_Double = QVariant.Type.Double
    QVariant_String = QVariant.Type.String

    # Qgis enums
    Qgis_Info = Qgis.MessageLevel.Info
    Qgis_Warning = Qgis.MessageLevel.Warning
    Qgis_Critical = Qgis.MessageLevel.Critical
    Qgis_Success = Qgis.MessageLevel.Success
    Qgis_Float32 = Qgis.DataType.Float32

    # QgsWkbTypes
    QgsWkbTypes_Point = QgsWkbTypes.Type.Point

else:
    # Qt5 style - simple enum access
    Qt_UserRole = Qt.UserRole
    Qt_RightDockWidgetArea = Qt.RightDockWidgetArea
    Qt_LeftDockWidgetArea = Qt.LeftDockWidgetArea

    # QVariant types
    QVariant_Int = QVariant.Int
    QVariant_Double = QVariant.Double
    QVariant_String = QVariant.String

    # Qgis enums
    Qgis_Info = Qgis.Info
    Qgis_Warning = Qgis.Warning
    Qgis_Critical = Qgis.Critical
    Qgis_Success = Qgis.Success
    Qgis_Float32 = Qgis.Float32

    # QgsWkbTypes
    QgsWkbTypes_Point = QgsWkbTypes.Point


def exec_dialog(dialog):
    """
    Execute a dialog in a Qt5/Qt6 compatible way.
    Qt6 removed exec_() in favor of exec()
    """
    if hasattr(dialog, 'exec'):
        return dialog.exec()
    else:
        return dialog.exec_()
