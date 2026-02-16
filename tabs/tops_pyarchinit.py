# -*- coding: utf-8 -*-
"""
/***************************************************************************
 TotalopenstationDialog
                                 A QGIS plugin
 Total Open Station (TOPS for friends) is a free software program for
 downloading and processing data from total station devices.
                             -------------------
        begin                : 2021-09-01
        copyright            : (C) 2021 by Enzo Cocca adArte srl; Stefano Costa
        email                : enzo.ccc@gmail.com
 ***************************************************************************/
/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
import importlib
import os
import csv
import sys
from datetime import date

import pandas as pd
from qgis.PyQt.QtGui import QStandardItemModel, QStandardItem
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtWidgets import (QDialog, QMessageBox, QFileDialog,
                                  QInputDialog)
from qgis.core import (QgsProject, QgsVectorLayer, QgsSettings)
from qgis.utils import iface
from qgis.PyQt.uic import loadUiType

MAIN_DIALOG_CLASS, _ = loadUiType(
    os.path.join(os.path.dirname(__file__), os.pardir, 'gui', 'ui', 'Tops2pyarchinit.ui'))

# Ensure totalopenstation is importable
TOPS_PATH = os.path.join(os.path.expanduser("~"), "Documents", "totalopenstation")
if os.path.isdir(TOPS_PATH) and TOPS_PATH not in sys.path:
    sys.path.insert(0, TOPS_PATH)


class pyarchinit_TOPS(QDialog, MAIN_DIALOG_CLASS):
    HOME = os.environ.get('PYARCHINIT_HOME', os.path.expanduser("~"))
    BIN = os.path.join(HOME, "pyarchinit_DB_folder")

    def __init__(self, iface):
        super().__init__()
        self.iface = iface
        self.setupUi(self)
        self.model = QStandardItemModel(self)
        self.tableView.setModel(self.model)
        self.toolButton_input.clicked.connect(self.setPathinput)
        self.toolButton_output.clicked.connect(self.setPathoutput)

    def setPathinput(self):
        s = QgsSettings()
        input_, _ = QFileDialog.getOpenFileName(self, "Set file name", '', "(*.*)")
        if input_:
            self.lineEdit_input.setText(input_)

    def setPathoutput(self):
        output_fmt = self.comboBox_format2.currentText()
        ext = output_fmt.split()[-1] if ' ' in output_fmt else output_fmt
        output_, _ = QFileDialog.getSaveFileName(self, "Set file name", '', f"(*.{ext})")
        if output_:
            self.lineEdit_output.setText(output_)

    def loadCsv(self, fileName):
        self.tableView.clearSpans()
        with open(fileName, "r") as fileInput:
            for row in csv.reader(fileInput):
                items = [QStandardItem(field) for field in row]
                self.model.appendRow(items)

    def delete(self):
        if self.tableView.selectionModel().hasSelection():
            from qgis.PyQt.QtCore import QPersistentModelIndex
            indexes = [QPersistentModelIndex(index)
                       for index in self.tableView.selectionModel().selectedRows()]
            for index in indexes:
                self.model.removeRow(index.row())

    def convert_csv(self):
        try:
            df = pd.read_csv(str(self.lineEdit_output.text()))
            df[['area_q', 'point_name']] = df['point_name'].str.split('-', expand=True)
            df.to_csv(str(self.lineEdit_output.text()), encoding='utf-8', index=False)
        except Exception:
            pass

    def _parse_and_export(self, input_file, output_file, input_format, output_format):
        """Parse input file and export using totalopenstation Python API."""
        try:
            import totalopenstation.formats
            import totalopenstation.output
        except ImportError:
            raise ImportError(
                "totalopenstation non trovato.\n"
                f"Verificare che sia presente in: {TOPS_PATH}\n"
                "Oppure installare con: pip install totalopenstation")

        # Read input file
        with open(input_file, 'r') as f:
            raw_data = f.read()

        # Auto-detect format if requested
        if input_format == 'auto-detect':
            try:
                from totalopenstation.formats.detect import detect_format
                detected = detect_format(raw_data)
                if detected is None:
                    raise ValueError(
                        "Impossibile determinare automaticamente il formato.\n"
                        "Selezionare il formato manualmente.")
                input_format = detected
            except ImportError:
                raise ImportError("Il modulo detect non è disponibile in questa versione di totalopenstation.")

        # Get input parser
        if input_format not in totalopenstation.formats.BUILTIN_INPUT_FORMATS:
            raise ValueError(f"Formato di input non supportato: {input_format}")

        fmt_info = totalopenstation.formats.BUILTIN_INPUT_FORMATS[input_format]
        mod_name, cls_name, _ = fmt_info
        input_module = importlib.import_module(f'totalopenstation.formats.{mod_name}')
        parser_class = getattr(input_module, cls_name)

        # Parse
        parser = parser_class(raw_data)
        points = parser.points

        if not points:
            raise ValueError("Nessun punto trovato nel file di input.")

        # For pyarchinit-specific CSV outputs, generate CSV directly
        if output_format.startswith('csv pyarchinit'):
            self._export_pyarchinit_csv(points, output_file)
        else:
            # Use TOPS output format
            tops_format = output_format
            if tops_format not in totalopenstation.output.BUILTIN_OUTPUT_FORMATS:
                raise ValueError(f"Formato di output non supportato: {tops_format}")

            out_info = totalopenstation.output.BUILTIN_OUTPUT_FORMATS[tops_format]
            out_mod, out_cls, _ = out_info
            output_module = importlib.import_module(f'totalopenstation.output.{out_mod}')
            output_class = getattr(output_module, out_cls)

            builder = output_class(points)
            result = builder.process()

            with open(output_file, 'w') as f:
                f.write(result)

        return len(points)

    def _export_pyarchinit_csv(self, points, output_file):
        """Export points to pyarchinit-compatible CSV format."""
        with open(output_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['point_name', 'x', 'y', 'z', 'desc'])
            for pt in points:
                geom = pt.geometry
                coords = geom.get('coordinates', [0, 0, 0]) if isinstance(geom, dict) else [0, 0, 0]
                x = coords[0] if len(coords) > 0 else 0
                y = coords[1] if len(coords) > 1 else 0
                z = coords[2] if len(coords) > 2 else 0
                props = pt.properties if hasattr(pt, 'properties') else {}
                name = props.get('point_name', props.get('desc', ''))
                desc = props.get('desc', '')
                writer.writerow([name, x, y, z, desc])

    def _load_csv_as_layer(self, output_file, layer_name):
        """Load a CSV file as a QGIS vector layer."""
        uri = f"file:///{output_file}?type=csv&xField=x&yField=y&spatialIndex=yes&subsetIndex=yes&watchFile=no"
        layer = QgsVectorLayer(uri, layer_name, "delimitedtext")
        if layer.isValid():
            QgsProject.instance().addMapLayer(layer)
            return layer
        return None

    def _copy_features_to_dest(self, source_layer, dest_layer_name, site_name,
                                set_attrs_fn):
        """Copy features from source to destination layer with attribute mapping."""
        try:
            dest_layer = QgsProject.instance().mapLayersByName(dest_layer_name)[0]
        except (IndexError, Exception):
            QMessageBox.warning(self, 'Total Open Station',
                                f"Layer '{dest_layer_name}' non trovato nel progetto.",
                                QMessageBox.StandardButton.Ok)
            return

        features = []
        for feature in source_layer.getFeatures():
            set_attrs_fn(feature)
            source_layer.updateFeature(feature)
            features.append(feature)

        dest_layer.startEditing()
        dest_layer.dataProvider().addFeatures(features)
        iface.mapCanvas().zoomToSelected()
        dest_layer.commitChanges()

    def on_pushButton_export_pressed(self):
        self.delete()

        input_file = self.lineEdit_input.text().strip()
        output_file = self.lineEdit_output.text().strip()
        input_format = self.comboBox_format.currentText()
        output_format = self.comboBox_format2.currentText()

        if not input_file or not output_file:
            QMessageBox.warning(self, 'Total Open Station',
                                'Selezionare file di input e output.',
                                QMessageBox.StandardButton.Ok)
            return

        try:
            n_points = self._parse_and_export(input_file, output_file, input_format, output_format)

            QMessageBox.information(self, 'Total Open Station',
                                    f'{n_points} punti processati con successo.',
                                    QMessageBox.StandardButton.Ok)

            # For standard TOPS outputs, just load and show
            if not output_format.startswith('csv pyarchinit'):
                self.loadCsv(output_file) if output_file.endswith('.csv') else None
                return

            # PyArchInit-specific integration
            self.convert_csv()

            output_idx = self.comboBox_format2.currentIndex()

            if output_idx == 0:  # csv pyarchinit_us
                layer = self._load_csv_as_layer(output_file, "totalopenstation Pyarchinit Quote")
                if not layer:
                    return
                self.loadCsv(output_file)

                ID_Sito = QInputDialog.getText(None, 'Sito', 'Input Nome del sito archeologico')
                Sito = str(ID_Sito[0])
                ID_M = QInputDialog.getText(None, 'Unità di misura', 'Input tipo di unità di misura\n (ex: metri)')
                Misura = str(ID_M[0])
                ID_Disegnatore = QInputDialog.getText(None, 'Disegnatore', 'Input Nome del Disegnatore')
                Disegnatore = str(ID_Disegnatore[0])

                q = 0.0
                if self.checkBox_coord.isChecked():
                    ID_Z = QInputDialog.getText(None, 'Z', 'Input Elevation')
                    q = float(ID_Z[0])

                def set_us_attrs(feature):
                    feature.setAttribute('sito_q', Sito)
                    feature.setAttribute('unita_misu_q', Misura)
                    feature.setAttribute('x', str(date.today().isoformat()))
                    feature.setAttribute('y', Disegnatore)
                    if self.checkBox_coord.isChecked():
                        attr_Q = feature.attributes()[5]
                        feature.setAttribute('quota_q', q + float(attr_Q))

                self._copy_features_to_dest(layer, 'Quote US disegno', Sito, set_us_attrs)
                QgsProject.instance().removeMapLayer(layer)

            elif output_idx == 1:  # csv pyarchinit_rif
                layer = self._load_csv_as_layer(output_file, "totalopenstation Pyarchinit riferimento")
                if not layer:
                    return
                self.loadCsv(output_file)

                ID_Sito = QInputDialog.getText(None, 'Sito', 'Input Nome del sito archeologico')
                Sito = str(ID_Sito[0])

                q = 0.0
                if self.checkBox_coord.isChecked():
                    ID_Z = QInputDialog.getText(None, 'Z', 'Input Elevation')
                    q = float(ID_Z[0])

                def set_rif_attrs(feature):
                    feature.setAttribute('sito', Sito)
                    if self.checkBox_coord.isChecked():
                        attr_Q = feature.attributes()[4]
                        feature.setAttribute('quota', q + float(attr_Q))

                self._copy_features_to_dest(layer, 'Punti di riferimento', Sito, set_rif_attrs)
                QgsProject.instance().removeMapLayer(layer)

            elif output_idx == 2:  # csv pyarchinit_sample
                layer = self._load_csv_as_layer(output_file, "totalopenstation Pyarchinit Sample")
                if not layer:
                    return
                self.loadCsv(output_file)

                ID_Sito = QInputDialog.getText(None, 'Sito', 'Input Nome del sito archeologico')
                Sito = str(ID_Sito[0])

                def set_sample_attrs(feature):
                    feature.setAttribute('sito', Sito)

                self._copy_features_to_dest(layer, 'Punti di campionatura', Sito, set_sample_attrs)
                QgsProject.instance().removeMapLayer(layer)

        except Exception as e:
            QMessageBox.warning(self, 'Total Open Station',
                                f"Error:\n{str(e)}", QMessageBox.StandardButton.Ok)

    @staticmethod
    def rmvLyr(lyrname):
        qinst = QgsProject.instance()
        qinst.removeMapLayer(qinst.mapLayersByName(lyrname)[0].id())
