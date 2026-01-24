# -*- coding: utf-8 -*-
"""
GNA Export Dialog Controller

Provides the UI for exporting PyArchInit UT data to GNA GeoPackage format.
"""

import os
from datetime import datetime

from qgis.PyQt import uic
from qgis.PyQt.QtCore import Qt, QSettings
from qgis.PyQt.QtWidgets import (
    QDialog,
    QFileDialog,
    QMessageBox,
    QApplication
)
from qgis.core import (
    QgsProject,
    QgsVectorLayer,
    QgsWkbTypes,
    QgsCoordinateReferenceSystem,
    QgsMapLayerProxyModel
)
from qgis.gui import QgsMapLayerComboBox

from ..modules.gna import GNAExporter, GNA_LABELS
from ..modules.gna.gna_labels import get_label

# Load UI file
FORM_CLASS, _ = uic.loadUiType(
    os.path.join(os.path.dirname(__file__), '..', 'gui', 'ui', 'GNA_export.ui')
)


class GNAExportDialog(QDialog, FORM_CLASS):
    """
    Dialog for exporting UT data to GNA GeoPackage.
    """

    def __init__(self, iface, db_manager, ut_records, project_name, parent=None):
        """
        Initialize the GNA export dialog.

        Args:
            iface: QGIS interface
            db_manager: PyArchInit database manager
            ut_records: List of UT records to export
            project_name: Current project name
            parent: Parent widget
        """
        super().__init__(parent)
        self.setupUi(self)

        self.iface = iface
        self.db_manager = db_manager
        self.ut_records = ut_records
        self.project_name = project_name
        self.result = None
        self.selected_polygon = None

        # Get language from settings
        self.language = self._get_language()

        # Initialize UI
        self._setup_ui()
        self._connect_signals()
        self._translate_ui()
        self._load_polygon_layers()
        self._set_default_values()

    def _get_language(self):
        """Get language code from QGIS settings."""
        settings = QSettings()
        locale = settings.value('locale/userLocale', 'it_IT')
        lang = locale.split('_')[0] if locale else 'it'
        return lang if lang in ('it', 'en', 'de', 'es', 'fr', 'ar', 'ca') else 'it'

    def _setup_ui(self):
        """Setup additional UI elements."""
        # Set window flags
        self.setWindowFlags(
            self.windowFlags() | Qt.WindowMaximizeButtonHint
        )

        # Configure OK button
        ok_button = self.buttonBox.button(self.buttonBox.Ok)
        ok_button.setText(get_label('btn_export', self.language))

        # Configure Cancel button
        cancel_button = self.buttonBox.button(self.buttonBox.Cancel)
        cancel_button.setText(get_label('btn_cancel', self.language))

    def _connect_signals(self):
        """Connect UI signals to handlers."""
        self.pushButton_browse.clicked.connect(self._on_browse_clicked)
        self.pushButton_select_from_map.clicked.connect(self._on_select_from_map)
        self.comboBox_polygon_layer.currentIndexChanged.connect(self._on_layer_changed)
        self.checkBox_vrp.toggled.connect(self._update_heatmap_options)
        self.checkBox_vrd.toggled.connect(self._update_heatmap_options)
        self.buttonBox.accepted.connect(self._on_export)
        self.buttonBox.rejected.connect(self.reject)

    def _translate_ui(self):
        """Apply translations to UI elements."""
        self.setWindowTitle(get_label('dialog_title', self.language))

        # Group boxes
        self.groupBox_project.setTitle(get_label('section_project', self.language))
        self.groupBox_area.setTitle(get_label('section_area', self.language))
        self.groupBox_layers.setTitle(get_label('section_layers', self.language))
        self.groupBox_heatmap.setTitle(get_label('section_options', self.language))
        self.groupBox_output.setTitle(get_label('section_output', self.language))

        # Labels
        self.label_project_code.setText(get_label('label_project_code', self.language))
        self.label_project_title.setText(get_label('label_project_title', self.language))
        self.label_responsible.setText(get_label('label_responsible', self.language))
        self.label_polygon_source.setText(get_label('label_from_layer', self.language))
        self.label_method.setText(get_label('label_method', self.language))
        self.label_cell_size.setText(get_label('label_cell_size', self.language))
        self.label_output_path.setText(get_label('label_output_path', self.language))

        # Checkboxes
        self.checkBox_mosi.setText(get_label('layer_mosi', self.language))
        self.checkBox_vrp.setText(get_label('layer_vrp', self.language))
        self.checkBox_vrd.setText(get_label('layer_vrd', self.language))
        self.checkBox_load_layers.setText(get_label('label_load_layers', self.language))

        # Buttons
        self.pushButton_browse.setText(get_label('browse', self.language))
        self.pushButton_select_from_map.setText(get_label('label_draw_polygon', self.language))

        # ComboBox items
        self.comboBox_method.setItemText(0, get_label('method_kde', self.language))
        self.comboBox_method.setItemText(1, get_label('method_idw', self.language))
        self.comboBox_method.setItemText(2, get_label('method_grid', self.language))

        # Tooltips
        self.checkBox_mosi.setToolTip(get_label('tooltip_mosi', self.language))
        self.checkBox_vrp.setToolTip(get_label('tooltip_vrp', self.language))
        self.checkBox_vrd.setToolTip(get_label('tooltip_vrd', self.language))

    def _load_polygon_layers(self):
        """Load available polygon layers into combo box."""
        self.comboBox_polygon_layer.clear()
        self.comboBox_polygon_layer.addItem("-- Select Layer --", None)

        for layer in QgsProject.instance().mapLayers().values():
            if isinstance(layer, QgsVectorLayer):
                if layer.geometryType() == QgsWkbTypes.PolygonGeometry:
                    self.comboBox_polygon_layer.addItem(layer.name(), layer.id())

    def _on_layer_changed(self, index):
        """Handle polygon layer selection change."""
        self.comboBox_polygon_feature.clear()

        layer_id = self.comboBox_polygon_layer.currentData()
        if not layer_id:
            return

        layer = QgsProject.instance().mapLayer(layer_id)
        if not layer:
            return

        # Populate feature combo
        for feat in layer.getFeatures():
            # Use feature ID or first attribute as label
            label = f"Feature {feat.id()}"
            if layer.fields():
                first_attr = feat[0] if feat[0] else f"ID: {feat.id()}"
                label = str(first_attr)[:50]
            self.comboBox_polygon_feature.addItem(label, feat.id())

    def _set_default_values(self):
        """Set default values in the form."""
        # Project info
        self.lineEdit_project_code.setText(self.project_name[:15].upper())
        self.lineEdit_project_title.setText(self.project_name)

        # Default output path
        home_dir = os.path.expanduser("~")
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        default_path = os.path.join(
            home_dir,
            f"GNA_{self.project_name}_{timestamp}.gpkg"
        )
        self.lineEdit_output_path.setText(default_path)

        # Status
        self.label_status.setText(
            f"Ready - {len(self.ut_records)} UT records"
        )

    def _on_browse_clicked(self):
        """Handle browse button click."""
        filepath, _ = QFileDialog.getSaveFileName(
            self,
            "Save GNA GeoPackage",
            self.lineEdit_output_path.text(),
            "GeoPackage (*.gpkg)"
        )
        if filepath:
            if not filepath.lower().endswith('.gpkg'):
                filepath += '.gpkg'
            self.lineEdit_output_path.setText(filepath)

    def _on_select_from_map(self):
        """Handle select from map button click."""
        QMessageBox.information(
            self,
            "Select Polygon",
            "Select a polygon feature on the map canvas, then return to this dialog."
        )
        # For now, use selected features from active layer
        active_layer = self.iface.activeLayer()
        if active_layer and isinstance(active_layer, QgsVectorLayer):
            selected = active_layer.selectedFeatures()
            if selected:
                self.selected_polygon = selected[0].geometry()
                self.label_status.setText(
                    f"Polygon selected from {active_layer.name()}"
                )

    def _update_heatmap_options(self):
        """Enable/disable heatmap options based on layer selection."""
        enabled = self.checkBox_vrp.isChecked() or self.checkBox_vrd.isChecked()
        self.groupBox_heatmap.setEnabled(enabled)

    def _get_selected_polygon(self):
        """Get the selected polygon geometry."""
        # Check if manually selected
        if self.selected_polygon:
            return self.selected_polygon

        # Get from combo boxes
        layer_id = self.comboBox_polygon_layer.currentData()
        feature_id = self.comboBox_polygon_feature.currentData()

        if not layer_id or feature_id is None:
            return None

        layer = QgsProject.instance().mapLayer(layer_id)
        if not layer:
            return None

        # Get feature
        for feat in layer.getFeatures():
            if feat.id() == feature_id:
                return feat.geometry()

        return None

    def _on_export(self):
        """Handle export button click."""
        # Validate inputs
        polygon = self._get_selected_polygon()
        if not polygon:
            QMessageBox.warning(
                self,
                "Warning",
                get_label('error_no_polygon', self.language)
            )
            return

        if not self.ut_records:
            QMessageBox.warning(
                self,
                "Warning",
                get_label('error_no_records', self.language)
            )
            return

        output_path = self.lineEdit_output_path.text()
        if not output_path:
            QMessageBox.warning(
                self,
                "Warning",
                "Please specify an output path"
            )
            return

        # Get options
        options = {
            'generate_mosi': self.checkBox_mosi.isChecked(),
            'generate_vrp': self.checkBox_vrp.isChecked(),
            'generate_vrd': self.checkBox_vrd.isChecked(),
            'heatmap_method': ['kde', 'idw', 'grid'][self.comboBox_method.currentIndex()],
            'cell_size': self.spinBox_cell_size.value(),
            'project_info': {
                'code': self.lineEdit_project_code.text(),
                'title': self.lineEdit_project_title.text(),
                'responsible': self.lineEdit_responsible.text(),
            },
        }

        # Start export
        self.label_status.setText(get_label('status_exporting', self.language))
        self.progressBar.setValue(10)
        QApplication.processEvents()

        try:
            # Create exporter
            exporter = GNAExporter(
                db_manager=self.db_manager,
                project_name=self.project_name,
                output_path=output_path,
                language=self.language
            )

            # Update progress
            self.label_status.setText(get_label('status_creating_mopr', self.language))
            self.progressBar.setValue(20)
            QApplication.processEvents()

            # Run export
            result = exporter.export(polygon, self.ut_records, options)

            self.progressBar.setValue(90)
            QApplication.processEvents()

            if result['success']:
                self.progressBar.setValue(100)
                self.label_status.setText(get_label('status_complete', self.language))

                # Load layers if requested
                if self.checkBox_load_layers.isChecked():
                    self._load_exported_layers(result['gpkg_path'], result['layers'])

                # Show success message
                QMessageBox.information(
                    self,
                    "GNA Export",
                    get_label('success_export', self.language).format(
                        result['gpkg_path'],
                        ', '.join(result['layers']),
                        result['record_count']
                    )
                )

                self.result = result
                self.accept()

            else:
                self.progressBar.setValue(0)
                self.label_status.setText("Export failed")
                error_msg = '\n'.join(result.get('errors', ['Unknown error']))
                QMessageBox.critical(
                    self,
                    "Export Error",
                    get_label('error_export_failed', self.language).format(error_msg)
                )

        except Exception as e:
            self.progressBar.setValue(0)
            self.label_status.setText("Export error")
            QMessageBox.critical(
                self,
                "Export Error",
                get_label('error_export_failed', self.language).format(str(e))
            )

    def _load_exported_layers(self, gpkg_path, layer_names):
        """Load exported layers into QGIS."""
        for layer_name in layer_names:
            uri = f"{gpkg_path}|layername={layer_name}"
            layer = QgsVectorLayer(uri, f"GNA_{layer_name}", 'ogr')
            if layer.isValid():
                QgsProject.instance().addMapLayer(layer)

    def get_result(self):
        """Get export result."""
        return self.result
