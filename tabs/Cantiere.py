#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
/***************************************************************************
        pyArchInit Plugin  - A QGIS plugin to manage archaeological dataset
                             stored in Postgres
                             -------------------
    begin                : 2007-12-01
    copyright            : (C) 2008 by Luca Mandolesi; Enzo Cocca <enzo.ccc@gmail.com>
    email                : mandoluca at gmail.com
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
from __future__ import absolute_import

import os
from datetime import datetime, date
from qgis.PyQt.QtWidgets import QDialog, QMessageBox, QTableWidgetItem, QHeaderView, QFileDialog
from qgis.PyQt.QtCore import Qt, QTimer
from qgis.PyQt.uic import loadUiType
from qgis.core import QgsSettings, QgsProject, QgsRasterLayer, QgsVectorLayer

from ..modules.utility.pyarchinit_theme_manager import ThemeManager
from ..modules.db.pyarchinit_conn_strings import Connection
from ..modules.db.pyarchinit_db_manager import get_db_manager
from ..modules.db.pyarchinit_utility import Utility

MAIN_DIALOG_CLASS, _ = loadUiType(
    os.path.join(os.path.dirname(__file__), os.pardir, 'gui', 'ui', 'Cantiere.ui'))


class pyarchinit_Cantiere(QDialog, MAIN_DIALOG_CLASS):
    L = QgsSettings().value("locale/userLocale", "it", type=str)[:2]
    DB_MANAGER = None
    DB_SERVER = "not defined"
    UTILITY = Utility()

    # i18n titles (10 languages)
    if L == 'it':
        MSG_BOX_TITLE = "PyArchInit - Dashboard Cantiere"
    elif L == 'en':
        MSG_BOX_TITLE = "PyArchInit - Site Dashboard"
    elif L == 'de':
        MSG_BOX_TITLE = "PyArchInit - Baustellen-Dashboard"
    elif L == 'es':
        MSG_BOX_TITLE = "PyArchInit - Panel de Obra"
    elif L == 'fr':
        MSG_BOX_TITLE = "PyArchInit - Tableau de Bord"
    elif L == 'ar':
        MSG_BOX_TITLE = "PyArchInit - \u0644\u0648\u062d\u0629 \u0627\u0644\u0642\u064a\u0627\u062f\u0629"
    elif L == 'ca':
        MSG_BOX_TITLE = "PyArchInit - Tauler d'Obra"
    elif L == 'ro':
        MSG_BOX_TITLE = "PyArchInit - Panou Santier"
    elif L == 'pt':
        MSG_BOX_TITLE = "PyArchInit - Painel de Obra"
    elif L == 'el':
        MSG_BOX_TITLE = "PyArchInit - \u03a0\u03af\u03bd\u03b1\u03ba\u03b1\u03c2 \u0395\u03c1\u03b3\u03bf\u03c4\u03b1\u03be\u03af\u03bf\u03c5"
    else:
        MSG_BOX_TITLE = "PyArchInit - Site Dashboard"

    def __init__(self, iface):
        super().__init__()
        self.iface = iface
        self.setupUi(self)
        ThemeManager.apply_theme(self)
        self.theme_toggle_btn = ThemeManager.add_theme_toggle_to_form(self)
        self.retranslate_ui()

        # Connect signals
        self.pushButton_refresh.clicked.connect(self.refresh_dashboard)
        self.pushButton_calcola.clicked.connect(self.on_pushButton_calcola_pressed)
        self.pushButton_salva_computo.clicked.connect(self.on_pushButton_salva_computo_pressed)
        self.comboBox_sito.currentTextChanged.connect(self.refresh_dashboard)
        self.comboBox_anno.currentTextChanged.connect(self.refresh_dashboard)
        self.pushButton_export_pdf.clicked.connect(self.on_pushButton_export_pdf_pressed)
        self.pushButton_export_excel.clicked.connect(self.on_pushButton_export_excel_pressed)

        # Defer DB loading so the window shows instantly
        QTimer.singleShot(0, self._deferred_init)

    def _deferred_init(self):
        """Load data after the window is visible."""
        try:
            self.on_pushButton_connect_pressed()
        except:
            pass
        self.charge_list()
        self.apply_sito_set()
        self.populate_raster_combos()
        self.populate_vector_combos()
        self.refresh_dashboard()

    def on_pushButton_connect_pressed(self):
        """Connect to database using singleton pattern"""
        conn = Connection()
        conn_str = conn.conn_str()
        test_conn = conn_str.find('sqlite')
        if test_conn == 0:
            self.DB_SERVER = "sqlite"
        try:
            self.DB_MANAGER = get_db_manager(conn_str, use_singleton=True)
        except Exception as e:
            QMessageBox.warning(self, "Connection Error", str(e))

    def charge_list(self):
        """Populate site and year dropdowns"""
        if not self.DB_MANAGER:
            return
        # Sites
        try:
            sito_vl = self.UTILITY.tup_2_list_III(
                self.DB_MANAGER.group_by('site_table', 'sito', 'SITE'))
            try:
                sito_vl.remove('')
            except:
                pass
            self.comboBox_sito.clear()
            sito_vl.sort()
            self.comboBox_sito.addItems(sito_vl)
        except:
            pass
        # Years
        current_year = date.today().year
        years = [str(y) for y in range(current_year, current_year - 10, -1)]
        self.comboBox_anno.clear()
        self.comboBox_anno.addItems(years)

    def apply_sito_set(self):
        """Pre-select the configured site if set"""
        try:
            conn = Connection()
            sito_set = conn.sito_set()
            sito_set_str = sito_set['sito_set']
            if bool(sito_set_str):
                idx = self.comboBox_sito.findText(sito_set_str)
                if idx >= 0:
                    self.comboBox_sito.setCurrentIndex(idx)
        except Exception:
            pass

    def populate_raster_combos(self):
        """Populate DEM layer comboboxes from QGIS project"""
        self.comboBox_dem_pre.clear()
        self.comboBox_dem_post.clear()
        self.comboBox_dem_pre.addItem("")
        self.comboBox_dem_post.addItem("")
        for layer_id, layer in QgsProject.instance().mapLayers().items():
            if isinstance(layer, QgsRasterLayer):
                self.comboBox_dem_pre.addItem(layer.name(), layer_id)
                self.comboBox_dem_post.addItem(layer.name(), layer_id)

    def populate_vector_combos(self):
        """Populate polygon layer combobox from QGIS project"""
        self.comboBox_layer_poligono.clear()
        self.comboBox_layer_poligono.addItem("")
        for layer_id, layer in QgsProject.instance().mapLayers().items():
            if isinstance(layer, QgsVectorLayer):
                self.comboBox_layer_poligono.addItem(layer.name(), layer_id)

    def retranslate_ui(self):
        """Translate all dashboard labels based on current locale."""
        lang = self.L
        t = {
            'it': {
                'title': 'pyArchInit - Dashboard Cantiere',
                'sito': 'Sito', 'anno': 'Anno',
                'budget_group': 'Riepilogo Budget',
                'budget_prev': 'Budget Previsto:', 'budget_spent': 'Budget Speso:',
                'personnel_group': 'Personale',
                'presenti': 'Presenti:', 'ferie': 'Ferie:', 'malattia': 'Malattia:',
                'ore_mese': 'Ore Totali:', 'costo_mese': 'Costo Totale:',
                'equip_group': 'Attrezzature',
                'totali': 'Totali:', 'in_uso': 'In Uso:', 'manutenzione': 'In Manutenzione:',
                'computo_group': 'Computo Metrico',
                'btn_calcola': 'Calcola', 'btn_salva': 'Salva Computo',
                'btn_refresh': 'Aggiorna', 'btn_pdf': 'Esporta PDF', 'btn_excel': 'Esporta CSV',
            },
            'en': {
                'title': 'pyArchInit - Site Dashboard',
                'sito': 'Site', 'anno': 'Year',
                'budget_group': 'Budget Summary',
                'budget_prev': 'Budget Forecast:', 'budget_spent': 'Budget Spent:',
                'personnel_group': 'Personnel',
                'presenti': 'Present:', 'ferie': 'On Leave:', 'malattia': 'Sick:',
                'ore_mese': 'Total Hours:', 'costo_mese': 'Total Cost:',
                'equip_group': 'Equipment',
                'totali': 'Total:', 'in_uso': 'In Use:', 'manutenzione': 'Under Maintenance:',
                'computo_group': 'Quantity Surveying',
                'btn_calcola': 'Calculate', 'btn_salva': 'Save Record',
                'btn_refresh': 'Refresh', 'btn_pdf': 'Export PDF', 'btn_excel': 'Export CSV',
            },
            'de': {
                'title': 'pyArchInit - Baustellen-Dashboard',
                'sito': 'Fundstelle', 'anno': 'Jahr',
                'budget_group': 'Budget-Übersicht',
                'budget_prev': 'Geplant:', 'budget_spent': 'Ausgegeben:',
                'personnel_group': 'Personal',
                'presenti': 'Anwesend:', 'ferie': 'Urlaub:', 'malattia': 'Krank:',
                'ore_mese': 'Stunden Gesamt:', 'costo_mese': 'Kosten Gesamt:',
                'equip_group': 'Ausrüstung',
                'totali': 'Gesamt:', 'in_uso': 'In Gebrauch:', 'manutenzione': 'In Wartung:',
                'computo_group': 'Mengenermittlung',
                'btn_calcola': 'Berechnen', 'btn_salva': 'Speichern',
                'btn_refresh': 'Aktualisieren', 'btn_pdf': 'PDF Export', 'btn_excel': 'CSV Export',
            },
            'es': {
                'title': 'pyArchInit - Panel de Obra',
                'sito': 'Sitio', 'anno': 'Año',
                'budget_group': 'Resumen de Presupuesto',
                'budget_prev': 'Previsto:', 'budget_spent': 'Gastado:',
                'personnel_group': 'Personal',
                'presenti': 'Presentes:', 'ferie': 'Vacaciones:', 'malattia': 'Baja:',
                'ore_mese': 'Horas Totales:', 'costo_mese': 'Coste Total:',
                'equip_group': 'Equipamiento',
                'totali': 'Total:', 'in_uso': 'En Uso:', 'manutenzione': 'En Mantenimiento:',
                'computo_group': 'Mediciones',
                'btn_calcola': 'Calcular', 'btn_salva': 'Guardar',
                'btn_refresh': 'Actualizar', 'btn_pdf': 'Exportar PDF', 'btn_excel': 'Exportar CSV',
            },
            'fr': {
                'title': 'pyArchInit - Tableau de Bord',
                'sito': 'Site', 'anno': 'Année',
                'budget_group': 'Résumé Budget',
                'budget_prev': 'Prévu:', 'budget_spent': 'Dépensé:',
                'personnel_group': 'Personnel',
                'presenti': 'Présents:', 'ferie': 'Congé:', 'malattia': 'Maladie:',
                'ore_mese': 'Heures Totales:', 'costo_mese': 'Coût Total:',
                'equip_group': 'Équipement',
                'totali': 'Total:', 'in_uso': 'En Usage:', 'manutenzione': 'En Maintenance:',
                'computo_group': 'Métré',
                'btn_calcola': 'Calculer', 'btn_salva': 'Enregistrer',
                'btn_refresh': 'Actualiser', 'btn_pdf': 'Exporter PDF', 'btn_excel': 'Exporter CSV',
            },
            'ar': {
                'title': 'pyArchInit - لوحة القيادة',
                'sito': 'الموقع', 'anno': 'السنة',
                'budget_group': 'ملخص الميزانية',
                'budget_prev': 'المخطط:', 'budget_spent': 'المنفق:',
                'personnel_group': 'الموظفون',
                'presenti': 'حاضرون:', 'ferie': 'إجازة:', 'malattia': 'مرضى:',
                'ore_mese': 'إجمالي الساعات:', 'costo_mese': 'إجمالي التكلفة:',
                'equip_group': 'المعدات',
                'totali': 'الإجمالي:', 'in_uso': 'قيد الاستخدام:', 'manutenzione': 'قيد الصيانة:',
                'computo_group': 'حساب الكميات',
                'btn_calcola': 'احسب', 'btn_salva': 'احفظ',
                'btn_refresh': 'تحديث', 'btn_pdf': 'تصدير PDF', 'btn_excel': 'تصدير CSV',
            },
            'ca': {
                'title': "pyArchInit - Tauler d'Obra",
                'sito': 'Lloc', 'anno': 'Any',
                'budget_group': 'Resum Pressupost',
                'budget_prev': 'Previst:', 'budget_spent': 'Gastat:',
                'personnel_group': 'Personal',
                'presenti': 'Presents:', 'ferie': 'Vacances:', 'malattia': 'Malaltia:',
                'ore_mese': 'Hores Totals:', 'costo_mese': 'Cost Total:',
                'equip_group': 'Equipament',
                'totali': 'Total:', 'in_uso': 'En Ús:', 'manutenzione': 'En Manteniment:',
                'computo_group': 'Amidament',
                'btn_calcola': 'Calcular', 'btn_salva': 'Desar',
                'btn_refresh': 'Actualitzar', 'btn_pdf': 'Exportar PDF', 'btn_excel': 'Exportar CSV',
            },
            'ro': {
                'title': 'pyArchInit - Panou Șantier',
                'sito': 'Sit', 'anno': 'An',
                'budget_group': 'Rezumat Buget',
                'budget_prev': 'Planificat:', 'budget_spent': 'Cheltuit:',
                'personnel_group': 'Personal',
                'presenti': 'Prezenți:', 'ferie': 'Concediu:', 'malattia': 'Medical:',
                'ore_mese': 'Ore Totale:', 'costo_mese': 'Cost Total:',
                'equip_group': 'Echipamente',
                'totali': 'Total:', 'in_uso': 'În Uz:', 'manutenzione': 'În Întreținere:',
                'computo_group': 'Măsurători',
                'btn_calcola': 'Calculează', 'btn_salva': 'Salvează',
                'btn_refresh': 'Actualizează', 'btn_pdf': 'Export PDF', 'btn_excel': 'Export CSV',
            },
            'pt': {
                'title': 'pyArchInit - Painel de Obra',
                'sito': 'Sítio', 'anno': 'Ano',
                'budget_group': 'Resumo Orçamento',
                'budget_prev': 'Previsto:', 'budget_spent': 'Gasto:',
                'personnel_group': 'Pessoal',
                'presenti': 'Presentes:', 'ferie': 'Férias:', 'malattia': 'Baixa:',
                'ore_mese': 'Horas Totais:', 'costo_mese': 'Custo Total:',
                'equip_group': 'Equipamento',
                'totali': 'Total:', 'in_uso': 'Em Uso:', 'manutenzione': 'Em Manutenção:',
                'computo_group': 'Medição',
                'btn_calcola': 'Calcular', 'btn_salva': 'Guardar',
                'btn_refresh': 'Atualizar', 'btn_pdf': 'Exportar PDF', 'btn_excel': 'Exportar CSV',
            },
            'el': {
                'title': 'pyArchInit - Πίνακας Εργοταξίου',
                'sito': 'Τοποθεσία', 'anno': 'Έτος',
                'budget_group': 'Σύνοψη Προϋπολογισμού',
                'budget_prev': 'Προβλεπόμενο:', 'budget_spent': 'Δαπανηθέν:',
                'personnel_group': 'Προσωπικό',
                'presenti': 'Παρόντες:', 'ferie': 'Άδεια:', 'malattia': 'Ασθένεια:',
                'ore_mese': 'Σύνολο Ωρών:', 'costo_mese': 'Συνολικό Κόστος:',
                'equip_group': 'Εξοπλισμός',
                'totali': 'Σύνολο:', 'in_uso': 'Σε Χρήση:', 'manutenzione': 'Σε Συντήρηση:',
                'computo_group': 'Επιμετρήσεις',
                'btn_calcola': 'Υπολογισμός', 'btn_salva': 'Αποθήκευση',
                'btn_refresh': 'Ανανέωση', 'btn_pdf': 'Εξαγωγή PDF', 'btn_excel': 'Εξαγωγή CSV',
            },
        }.get(lang, None)
        if t is None:
            t = {  # fallback to English
                'title': 'pyArchInit - Site Dashboard',
                'sito': 'Site', 'anno': 'Year',
                'budget_group': 'Budget Summary', 'budget_prev': 'Budget Forecast:', 'budget_spent': 'Budget Spent:',
                'personnel_group': 'Personnel',
                'presenti': 'Present:', 'ferie': 'On Leave:', 'malattia': 'Sick:',
                'ore_mese': 'Total Hours:', 'costo_mese': 'Total Cost:',
                'equip_group': 'Equipment',
                'totali': 'Total:', 'in_uso': 'In Use:', 'manutenzione': 'Under Maintenance:',
                'computo_group': 'Quantity Surveying',
                'btn_calcola': 'Calculate', 'btn_salva': 'Save Record',
                'btn_refresh': 'Refresh', 'btn_pdf': 'Export PDF', 'btn_excel': 'Export CSV',
            }
        self.setWindowTitle(t['title'])
        self.label_sito.setText(t['sito'])
        self.label_anno.setText(t['anno'])
        self.groupBox_riepilogo_budget.setTitle(t['budget_group'])
        self.label_lbl_budget_previsto.setText(t['budget_prev'])
        self.label_lbl_budget_speso.setText(t['budget_spent'])
        self.groupBox_personale_oggi.setTitle(t['personnel_group'])
        self.label_lbl_presenti.setText(t['presenti'])
        self.label_lbl_ferie.setText(t['ferie'])
        self.label_lbl_malattia.setText(t['malattia'])
        self.label_lbl_ore_mese.setText(t['ore_mese'])
        self.label_lbl_costo_mese.setText(t['costo_mese'])
        self.groupBox_attrezzature.setTitle(t['equip_group'])
        self.label_lbl_totali.setText(t['totali'])
        self.label_lbl_in_uso.setText(t['in_uso'])
        self.label_lbl_manutenzione.setText(t['manutenzione'])
        self.groupBox_computo_metrico.setTitle(t['computo_group'])
        self.pushButton_calcola.setText(t['btn_calcola'])
        self.pushButton_salva_computo.setText(t['btn_salva'])
        self.pushButton_refresh.setText(t['btn_refresh'])
        self.pushButton_export_pdf.setText(t['btn_pdf'])
        self.pushButton_export_excel.setText(t['btn_excel'])

    def refresh_dashboard(self):
        """Refresh all dashboard sections"""
        sito = self.comboBox_sito.currentText()
        anno = self.comboBox_anno.currentText()
        if not sito or not self.DB_MANAGER:
            return
        self.refresh_budget_summary(sito, anno)
        self.refresh_personnel_summary(sito)
        self.refresh_equipment_summary(sito)
        self.refresh_computo_history(sito)

    def refresh_budget_summary(self, sito, anno):
        """Query budget_table, calculate totals, update progress bar"""
        try:
            search_dict = {'sito': "'" + sito + "'"}
            if anno and anno.strip():
                try:
                    search_dict['anno'] = int(anno)
                except ValueError:
                    pass
            records = self.DB_MANAGER.query_bool(search_dict, 'BUDGET')

            totale_previsto = sum(r.importo_previsto or 0 for r in records)
            totale_effettivo = sum(r.importo_effettivo or 0 for r in records)

            self.label_budget_previsto.setText(f"\u20ac {totale_previsto:,.2f}")
            self.label_budget_speso.setText(f"\u20ac {totale_effettivo:,.2f}")

            if totale_previsto > 0:
                pct = int((totale_effettivo / totale_previsto) * 100)
                self.progressBar_budget.setValue(min(pct, 100))
            else:
                self.progressBar_budget.setValue(0)

            # Draw pie chart
            self.draw_budget_chart(records)
        except Exception as e:
            pass

    # Multilingual terms for filtering attendance and equipment records (10 languages)
    # it, en, de, es, fr, ar, ca, ro, pt, el
    WORKING_DAY_TERMS = {
        'ordinaria', 'regular day', 'regulärer tag', 'jornada ordinaria',
        'journée ordinaire', 'يوم عادي', 'jornada ordinària', 'zi normală',
        'dia regular', 'κανονική ημέρα',
        'regular', 'overtime day', 'straordinaria', 'half day', 'mezza giornata',
        'training day', 'formazione', 'überstundentag', 'jornada extraordinaria',
        'journée supplémentaire', 'يوم إضافي', 'jornada extraordinària', 'zi cu ore suplimentare',
        'dia de horas extra', 'υπερωριακή ημέρα',
        'halber tag', 'media jornada', 'demi-journée', 'نصف يوم', 'mitja jornada',
        'jumătate de zi', 'meio dia', 'μισή ημέρα',
        'schulungstag', 'día de formación', 'journée de formation', 'يوم تدريب',
        'jornada de formació', 'zi de formare', 'dia de formação', 'ημέρα εκπαίδευσης',
        'trasferta', 'travel day', 'reisetag', 'día de viaje', 'journée de déplacement',
        'يوم سفر', 'jornada de viatge', 'zi de deplasare', 'dia de viagem', 'ημέρα μετακίνησης',
    }
    HOLIDAY_TERMS = {
        'ferie', 'holiday', 'holiday/leave', 'urlaub', 'vacaciones', 'congé', 'إجازة',
        'vacances', 'concediu', 'férias', 'άδεια',
    }
    SICK_TERMS = {
        'malattia', 'sick leave', 'krankheit', 'baja médica', 'maladie', 'إجازة مرضية',
        'malaltia', 'concediu medical', 'baixa médica', 'αναρρωτική',
    }
    DAYOFF_TERMS = {
        'permesso', 'day off', 'freistellung', 'permiso', 'permission', 'إذن',
        'permís', 'permisie', 'licença', 'ρεπό',
        'festivo', 'public holiday', 'feiertag', 'festivo', 'jour férié', 'يوم عطلة',
        'festiu', 'zi liberă', 'feriado', 'αργία',
        'assente', 'absent', 'abwesend', 'ausente', 'absent', 'غائب',
        'absent', 'absent', 'ausente', 'απών',
    }
    IN_USE_TERMS = {
        'in uso', 'in use', 'in gebrauch', 'en uso', 'en utilisation', 'قيد الاستخدام',
        'en ús', 'în uz', 'em uso', 'σε χρήση',
    }
    MAINTENANCE_TERMS = {
        'in manutenzione', 'under maintenance', 'in wartung', 'en mantenimiento',
        'en maintenance', 'قيد الصيانة', 'en manteniment', 'în întreținere',
        'em manutenção', 'σε συντήρηση',
    }
    DECOMMISSIONED_TERMS = {
        'dismessa', 'decommissioned', 'fuori_uso', 'fuori uso', 'außer betrieb',
        'fuera de servicio', 'hors service', 'خارج الخدمة', 'fora de servei',
        'scos din uz', 'fora de serviço', 'εκτός λειτουργίας',
    }

    def refresh_personnel_summary(self, sito):
        """Query presenze_table - show all-time stats if no records today"""
        try:
            # First try today's records
            today = date.today().isoformat()
            search_dict = {'sito': "'" + sito + "'", 'data': "'" + today + "'"}
            records = self.DB_MANAGER.query_bool(search_dict, 'PRESENZE')

            # If no records today, show all records for the site
            if not records:
                search_dict = {'sito': "'" + sito + "'"}
                records = self.DB_MANAGER.query_bool(search_dict, 'PRESENZE')

            presenti = sum(1 for r in records if r.tipo_giornata and r.tipo_giornata.lower() in self.WORKING_DAY_TERMS)
            ferie = sum(1 for r in records if r.tipo_giornata and r.tipo_giornata.lower() in self.HOLIDAY_TERMS)
            malattia = sum(1 for r in records if r.tipo_giornata and r.tipo_giornata.lower() in self.SICK_TERMS)

            self.label_presenti.setText(str(presenti))
            self.label_ferie.setText(str(ferie))
            self.label_malattia.setText(str(malattia))

            # Monthly totals - use current month or latest month with data
            month_prefix = today[:7]  # YYYY-MM
            search_all = {'sito': "'" + sito + "'"}
            all_records = self.DB_MANAGER.query_bool(search_all, 'PRESENZE')
            month_records = [r for r in all_records if r.data and r.data.startswith(month_prefix)]

            # If no records this month, use all records
            if not month_records:
                month_records = all_records

            ore_mese = sum(r.ore_ordinarie or 0 for r in month_records) + sum(r.ore_straordinario or 0 for r in month_records)
            costo_mese = sum(r.costo_giornata or 0 for r in month_records)

            self.label_ore_mese.setText(f"{ore_mese:.1f}")
            self.label_costo_mese.setText(f"\u20ac {costo_mese:,.2f}")
        except:
            pass

    def refresh_equipment_summary(self, sito):
        """Query attrezzature_table"""
        try:
            search_dict = {'sito': "'" + sito + "'"}
            records = self.DB_MANAGER.query_bool(search_dict, 'ATTREZZATURE')

            totali = len(records)
            in_uso = sum(1 for r in records if r.stato and r.stato.lower() in self.IN_USE_TERMS)
            manutenzione = sum(1 for r in records if r.stato and r.stato.lower() in self.MAINTENANCE_TERMS)

            self.label_totali.setText(str(totali))
            self.label_in_uso.setText(str(in_uso))
            self.label_manutenzione.setText(str(manutenzione))

            # Check overdue maintenance
            today = date.today().isoformat()
            overdue = [r for r in records if r.data_prossima_manutenzione and r.data_prossima_manutenzione < today
                       and not (r.stato and r.stato.lower() in self.DECOMMISSIONED_TERMS)]
            if overdue:
                alert_msgs = {'it': 'scadenze manutenzione!', 'en': 'maintenance overdue!',
                              'de': 'Wartung überfällig!', 'es': 'mantenimiento vencido!',
                              'fr': 'maintenance en retard!', 'ar': 'صيانة متأخرة!'}
                msg = alert_msgs.get(self.L, alert_msgs['en'])
                self.label_alert_manutenzione.setText(f"⚠ {len(overdue)} {msg}")
                self.label_alert_manutenzione.setStyleSheet("color: red; font-weight: bold;")
            else:
                ok_msgs = {'it': 'Nessuna scadenza', 'en': 'No overdue', 'de': 'Keine Überfälligkeiten',
                           'es': 'Sin vencimientos', 'fr': 'Aucun retard', 'ar': 'لا تأخير'}
                self.label_alert_manutenzione.setText(ok_msgs.get(self.L, ok_msgs['en']))
                self.label_alert_manutenzione.setStyleSheet("color: green;")
        except:
            pass

    def refresh_computo_history(self, sito):
        """Load computo metrico history into table widget"""
        try:
            search_dict = {'sito': "'" + sito + "'"}
            records = self.DB_MANAGER.query_bool(search_dict, 'COMPUTO_METRICO')

            self.tableWidget_computi.setRowCount(0)
            for r in records:
                row = self.tableWidget_computi.rowCount()
                self.tableWidget_computi.insertRow(row)
                self.tableWidget_computi.setItem(row, 0, QTableWidgetItem(str(r.data_calcolo or '')))
                self.tableWidget_computi.setItem(row, 1, QTableWidgetItem(str(r.tipo_calcolo or '')))
                self.tableWidget_computi.setItem(row, 2, QTableWidgetItem(f"{r.area_mq or 0:.2f}"))
                self.tableWidget_computi.setItem(row, 3, QTableWidgetItem(f"{r.volume_mc or 0:.2f}"))
                self.tableWidget_computi.setItem(row, 4, QTableWidgetItem(str(r.note or '')))
        except:
            pass

    def on_pushButton_calcola_pressed(self):
        """Calculate area/volume from DEM layers"""
        if self.radioButton_diff_dem.isChecked():
            self.calculate_dem_difference()
        else:
            self.calculate_dem_polygon()

    def calculate_dem_difference(self):
        """Calculate volume from difference of two DEMs"""
        try:
            from qgis.analysis import QgsRasterCalculator, QgsRasterCalculatorEntry
            import tempfile

            layer_pre_id = self.comboBox_dem_pre.currentData()
            layer_post_id = self.comboBox_dem_post.currentData()

            if not layer_pre_id or not layer_post_id:
                QMessageBox.warning(self, self.MSG_BOX_TITLE, "Select both DEM layers")
                return

            layer_pre = QgsProject.instance().mapLayer(layer_pre_id)
            layer_post = QgsProject.instance().mapLayer(layer_post_id)

            if not layer_pre or not layer_post:
                QMessageBox.warning(self, self.MSG_BOX_TITLE, "Could not load DEM layers")
                return

            # Use raster calculator to compute difference
            extent = layer_pre.extent()
            pixel_x = layer_pre.rasterUnitsPerPixelX()
            pixel_y = layer_pre.rasterUnitsPerPixelY()
            n_cols = layer_pre.width()
            n_rows = layer_pre.height()

            entries = []
            entry_pre = QgsRasterCalculatorEntry()
            entry_pre.ref = 'pre@1'
            entry_pre.raster = layer_pre
            entry_pre.bandNumber = 1
            entries.append(entry_pre)

            entry_post = QgsRasterCalculatorEntry()
            entry_post.ref = 'post@1'
            entry_post.raster = layer_post
            entry_post.bandNumber = 1
            entries.append(entry_post)

            output_path = os.path.join(tempfile.gettempdir(), 'pyarchinit_dem_diff.tif')
            formula = 'pre@1 - post@1'

            calc = QgsRasterCalculator(formula, output_path, 'GTiff',
                                        extent, n_cols, n_rows, entries)
            result = calc.processCalculation()

            if result == 0:
                # Load result and compute volume
                diff_layer = QgsRasterLayer(output_path, 'DEM_diff')
                provider = diff_layer.dataProvider()
                block = provider.block(1, extent, n_cols, n_rows)

                pixel_area = abs(pixel_x * pixel_y)
                total_volume = 0.0
                total_area = 0.0

                for row_idx in range(n_rows):
                    for col_idx in range(n_cols):
                        val = block.value(row_idx, col_idx)
                        if val and not block.isNoData(row_idx, col_idx):
                            total_volume += abs(val) * pixel_area
                            if abs(val) > 0.01:
                                total_area += pixel_area

                self.label_area_mq.setText(f"{total_area:.2f} m\u00b2")
                self.label_volume_mc.setText(f"{total_volume:.2f} m\u00b3")

                # Clean up temp file
                try:
                    os.remove(output_path)
                except:
                    pass
            else:
                QMessageBox.warning(self, self.MSG_BOX_TITLE, "Raster calculation failed")
        except Exception as e:
            QMessageBox.warning(self, self.MSG_BOX_TITLE, f"Error: {str(e)}")

    def calculate_dem_polygon(self):
        """Calculate volume/area from DEM within polygon"""
        try:
            from qgis.analysis import QgsZonalStatistics

            layer_dem_id = self.comboBox_dem_pre.currentData()
            layer_poly_id = self.comboBox_layer_poligono.currentData()

            if not layer_dem_id or not layer_poly_id:
                QMessageBox.warning(self, self.MSG_BOX_TITLE, "Select DEM and polygon layers")
                return

            layer_dem = QgsProject.instance().mapLayer(layer_dem_id)
            layer_poly = QgsProject.instance().mapLayer(layer_poly_id)

            if not layer_dem or not layer_poly:
                QMessageBox.warning(self, self.MSG_BOX_TITLE, "Could not load layers")
                return

            # Run zonal statistics
            zs = QgsZonalStatistics(layer_poly, layer_dem, 'dem_',
                                     1, QgsZonalStatistics.Sum | QgsZonalStatistics.Count |
                                     QgsZonalStatistics.Min | QgsZonalStatistics.Max)
            zs.calculateStatistics(None)

            # Read results from polygon features
            total_area = 0.0
            total_volume = 0.0
            quota_min = float('inf')
            quota_max = float('-inf')

            pixel_area = layer_dem.rasterUnitsPerPixelX() * layer_dem.rasterUnitsPerPixelY()

            for feat in layer_poly.getFeatures():
                count = feat['dem_count'] if feat['dem_count'] else 0
                dem_sum = feat['dem_sum'] if feat['dem_sum'] else 0
                dem_min = feat['dem_min'] if feat['dem_min'] else 0
                dem_max = feat['dem_max'] if feat['dem_max'] else 0

                total_area += count * pixel_area
                total_volume += abs(dem_sum) * pixel_area
                if dem_min < quota_min:
                    quota_min = dem_min
                if dem_max > quota_max:
                    quota_max = dem_max

            self.label_area_mq.setText(f"{total_area:.2f} m\u00b2")
            self.label_volume_mc.setText(f"{total_volume:.2f} m\u00b3")
        except Exception as e:
            QMessageBox.warning(self, self.MSG_BOX_TITLE, f"Error: {str(e)}")

    def on_pushButton_salva_computo_pressed(self):
        """Save computo metrico result to database"""
        try:
            sito = self.comboBox_sito.currentText()
            if not sito or not self.DB_MANAGER:
                return

            area_text = self.label_area_mq.text().replace(' m\u00b2', '').replace(' m2', '')
            volume_text = self.label_volume_mc.text().replace(' m\u00b3', '').replace(' m3', '')

            try:
                area_val = float(area_text)
                volume_val = float(volume_text)
            except ValueError:
                QMessageBox.warning(self, self.MSG_BOX_TITLE, "No calculation results to save")
                return

            tipo = 'differenza_dem' if self.radioButton_diff_dem.isChecked() else 'dem_poligono'
            dem_pre_name = self.comboBox_dem_pre.currentText()
            dem_post_name = self.comboBox_dem_post.currentText()
            poly_name = self.comboBox_layer_poligono.currentText()

            next_id = self.DB_MANAGER.max_num_id('COMPUTO_METRICO', 'id_computo') + 1

            data = self.DB_MANAGER.insert_computo_metrico_values(
                next_id,
                sito,
                f"Calcolo {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                tipo,
                dem_pre_name,
                dem_post_name,
                poly_name,
                area_val,
                volume_val,
                0.0,  # quota_min
                0.0,  # quota_max
                date.today().isoformat(),
                '',   # fase_scavo
                ''    # note
            )
            self.DB_MANAGER.insert_data_session(data)
            self.refresh_computo_history(sito)
            QMessageBox.information(self, self.MSG_BOX_TITLE, "Computo saved!")
        except Exception as e:
            QMessageBox.warning(self, self.MSG_BOX_TITLE, f"Error saving: {str(e)}")

    def _clear_chart_layout(self):
        """Clear existing widgets from widget_chart layout, creating one if needed."""
        from qgis.PyQt.QtWidgets import QVBoxLayout
        layout = self.widget_chart.layout()
        if layout is None:
            layout = QVBoxLayout(self.widget_chart)
            layout.setContentsMargins(0, 0, 0, 0)
        else:
            while layout.count():
                child = layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()
        return layout

    def _aggregate_budget_by_category(self, records):
        """Aggregate budget records by category, returning dict of {category: total}."""
        cat_totals = {}
        default_label = 'Altro' if self.L == 'it' else 'Other'
        for r in records:
            cat = r.categoria or default_label
            cat_totals[cat] = cat_totals.get(cat, 0) + (r.importo_effettivo or 0)
        return cat_totals

    def _get_chart_title(self):
        """Return locale-aware chart title."""
        titles = {
            'it': 'Budget per Categoria',
            'en': 'Budget by Category',
            'de': 'Budget nach Kategorie',
            'es': 'Presupuesto por Categoría',
            'fr': 'Budget par Catégorie',
            'ar': 'الميزانية حسب الفئة',
            'ca': 'Pressupost per Categoria',
            'ro': 'Buget pe Categorie',
            'pt': 'Orçamento por Categoria',
            'el': 'Προϋπολογισμός ανά Κατηγορία',
        }
        return titles.get(self.L, titles['en'])

    def draw_budget_chart(self, records):
        """Draw an interactive Plotly pie chart in QWebEngineView, with matplotlib fallback."""
        cat_totals = self._aggregate_budget_by_category(records)
        if not cat_totals or sum(cat_totals.values()) == 0:
            return

        # Try Plotly + QWebEngineView first
        if self._draw_budget_chart_plotly(cat_totals):
            return

        # Fallback to matplotlib
        self._draw_budget_chart_matplotlib(cat_totals)

    def _draw_budget_chart_plotly(self, cat_totals):
        """Render an interactive Plotly pie chart inside QWebEngineView. Returns True on success."""
        try:
            import plotly.graph_objects as go
        except ImportError:
            return False

        # Import QWebEngineView from multiple possible paths
        QWebEngineView = None
        for _import_path in [
            ('qgis.PyQt.QtWebEngineWidgets', 'QWebEngineView'),
            ('PyQt5.QtWebEngineWidgets', 'QWebEngineView'),
            ('PyQt6.QtWebEngineWidgets', 'QWebEngineView'),
        ]:
            try:
                mod = __import__(_import_path[0], fromlist=[_import_path[1]])
                QWebEngineView = getattr(mod, _import_path[1])
                break
            except (ImportError, AttributeError):
                continue

        if QWebEngineView is None:
            return False

        try:
            layout = self._clear_chart_layout()

            labels = list(cat_totals.keys())
            values = list(cat_totals.values())

            # Professional color palette (Material Design inspired)
            colors = [
                '#1565C0', '#00897B', '#EF6C00', '#6A1B9A',
                '#C62828', '#2E7D32', '#AD1457', '#4527A0',
                '#00838F', '#F9A825', '#4E342E',
            ]

            title_text = self._get_chart_title()

            fig = go.Figure(data=[go.Pie(
                labels=labels,
                values=values,
                hole=0.4,
                marker=dict(
                    colors=colors[:len(labels)],
                    line=dict(color='#ffffff', width=2),
                ),
                textinfo='label+percent',
                textfont=dict(size=11, family='Segoe UI, Helvetica, Arial, sans-serif'),
                hovertemplate='<b>%{label}</b><br>€ %{value:,.2f}<br>%{percent}<extra></extra>',
                sort=False,
            )])

            fig.update_layout(
                title=dict(
                    text=title_text,
                    font=dict(size=14, family='Segoe UI, Helvetica, Arial, sans-serif', color='#2c3e50'),
                    x=0.5,
                    xanchor='center',
                ),
                margin=dict(l=10, r=10, t=40, b=10),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                showlegend=True,
                legend=dict(
                    font=dict(size=10, family='Segoe UI, Helvetica, Arial, sans-serif'),
                    orientation='h',
                    yanchor='bottom',
                    y=-0.15,
                    xanchor='center',
                    x=0.5,
                ),
            )

            html_content = fig.to_html(
                include_plotlyjs='cdn',
                full_html=True,
                config={
                    'displayModeBar': False,
                    'responsive': True,
                },
            )

            # Inject responsive viewport meta and body style
            html_content = html_content.replace(
                '<head>',
                '<head><meta name="viewport" content="width=device-width, initial-scale=1">'
                '<style>body{margin:0;padding:0;overflow:hidden;}'
                '.plotly-graph-div{width:100%!important;height:100%!important;}</style>',
            )

            web_view = QWebEngineView()
            web_view.setHtml(html_content)
            layout.addWidget(web_view)
            return True

        except Exception:
            return False

    def _draw_budget_chart_matplotlib(self, cat_totals):
        """Fallback: render a matplotlib pie chart on a Qt canvas."""
        try:
            from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
            from matplotlib.figure import Figure

            layout = self._clear_chart_layout()

            fig = Figure(figsize=(4, 3), dpi=80)
            ax = fig.add_subplot(111)
            colors = ['#1565C0', '#00897B', '#EF6C00', '#6A1B9A',
                      '#C62828', '#2E7D32', '#AD1457', '#4527A0',
                      '#00838F', '#F9A825', '#4E342E']

            labels = list(cat_totals.keys())
            sizes = list(cat_totals.values())
            ax.pie(sizes, labels=labels, colors=colors[:len(labels)],
                   autopct='%1.0f%%', startangle=90, textprops={'fontsize': 7})
            ax.set_title(self._get_chart_title(), fontsize=9)
            ax.set_aspect('equal')
            fig.tight_layout()

            canvas = FigureCanvasQTAgg(fig)
            layout.addWidget(canvas)
            canvas.draw()
        except ImportError:
            pass
        except Exception:
            pass


    def on_pushButton_export_pdf_pressed(self):
        """Export a professional dashboard PDF with budget chart, personnel, and equipment."""
        sito = self.comboBox_sito.currentText()
        anno = self.comboBox_anno.currentText()
        if not sito:
            QMessageBox.warning(self, "Warning", "Select a site first.", QMessageBox.StandardButton.Ok)
            return

        home = os.environ.get('PYARCHINIT_HOME', os.path.expanduser('~'))
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export PDF",
            os.path.join(home, f"site_dashboard_{sito}_{anno}.pdf"), "PDF (*.pdf)")
        if not file_path:
            return

        try:
            from reportlab.lib import colors
            from reportlab.lib.pagesizes import A4
            from reportlab.lib.units import cm, mm
            from reportlab.platypus import (SimpleDocTemplate, Table, TableStyle,
                                            Paragraph, Spacer, PageBreak, KeepTogether)
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
            from reportlab.platypus.flowables import HRFlowable
            from reportlab.graphics.shapes import Drawing, Rect, String, Line, Group
            from reportlab.graphics import renderPDF
            from datetime import datetime

            lang = self.L
            page_w, page_h = A4  # 595.27, 841.89 points

            # --- Color scheme ---
            CLR_HEADER = colors.HexColor('#1a237e')
            CLR_ACCENT = colors.HexColor('#e3f2fd')
            CLR_ROW_ALT = colors.HexColor('#f5f7fa')
            CLR_TEXT_LIGHT = colors.white
            CLR_BORDER = colors.HexColor('#bbdefb')
            CLR_BUDGET = colors.HexColor('#1565c0')
            CLR_ACTUAL = colors.HexColor('#e65100')
            CLR_SUMMARY_BG = colors.HexColor('#e8eaf6')
            CLR_SECTION_LINE = colors.HexColor('#3949ab')

            # --- i18n ---
            i18n = {
                'it': {
                    'title': 'Dashboard Cantiere',
                    'subtitle': 'Riepilogo operativo del cantiere',
                    'site': 'Cantiere', 'year': 'Anno', 'generated': 'Generato il',
                    'budget_section': 'Riepilogo Budget',
                    'budget_headers': ['Categoria', 'Descrizione', 'Preventivato', 'Effettivo', 'Differenza'],
                    'total': 'TOTALE', 'budgeted': 'Preventivato', 'actual': 'Effettivo',
                    'personnel_section': 'Personale',
                    'pers_headers': ['Nome', 'Cognome', 'Ruolo', 'Contratto', 'Email', 'Tariffa Giorn.'],
                    'equip_section': 'Inventario Attrezzature',
                    'equip_headers': ['Codice', 'Nome', 'Categoria', 'Marca', 'Modello', 'Stato'],
                    'statistics': 'Statistiche',
                    'total_personnel': 'Totale Personale',
                    'total_equipment': 'Totale Attrezzature',
                    'budget_variance': 'Variazione Budget',
                    'budget_chart': 'Grafico Budget per Categoria',
                    'page': 'Pagina',
                    'footer': 'pyArchInit - Gestione Dati Archeologici',
                    'no_data': 'Nessun dato disponibile',
                },
                'en': {
                    'title': 'Site Dashboard',
                    'subtitle': 'Operational site summary',
                    'site': 'Site', 'year': 'Year', 'generated': 'Generated on',
                    'budget_section': 'Budget Summary',
                    'budget_headers': ['Category', 'Description', 'Budgeted', 'Actual', 'Variance'],
                    'total': 'TOTAL', 'budgeted': 'Budgeted', 'actual': 'Actual',
                    'personnel_section': 'Personnel',
                    'pers_headers': ['First Name', 'Last Name', 'Role', 'Contract', 'Email', 'Daily Rate'],
                    'equip_section': 'Equipment Inventory',
                    'equip_headers': ['Code', 'Name', 'Category', 'Brand', 'Model', 'Status'],
                    'statistics': 'Statistics',
                    'total_personnel': 'Total Personnel',
                    'total_equipment': 'Total Equipment',
                    'budget_variance': 'Budget Variance',
                    'budget_chart': 'Budget by Category',
                    'page': 'Page',
                    'footer': 'pyArchInit - Archaeological Data Management',
                    'no_data': 'No data available',
                },
                'de': {
                    'title': 'Fundstellen-Dashboard',
                    'subtitle': 'Operative Zusammenfassung',
                    'site': 'Fundstelle', 'year': 'Jahr', 'generated': 'Erstellt am',
                    'budget_section': 'Budgetubersicht',
                    'budget_headers': ['Kategorie', 'Beschreibung', 'Geplant', 'Tatsachlich', 'Differenz'],
                    'total': 'GESAMT', 'budgeted': 'Geplant', 'actual': 'Tatsachlich',
                    'personnel_section': 'Personal',
                    'pers_headers': ['Vorname', 'Nachname', 'Rolle', 'Vertrag', 'E-Mail', 'Tagessatz'],
                    'equip_section': 'Ausrustungsinventar',
                    'equip_headers': ['Code', 'Name', 'Kategorie', 'Marke', 'Modell', 'Status'],
                    'statistics': 'Statistiken',
                    'total_personnel': 'Gesamtpersonal',
                    'total_equipment': 'Gesamtausrustung',
                    'budget_variance': 'Budgetabweichung',
                    'budget_chart': 'Budget nach Kategorie',
                    'page': 'Seite',
                    'footer': 'pyArchInit - Archaologische Datenverwaltung',
                    'no_data': 'Keine Daten verfugbar',
                },
                'es': {
                    'title': 'Panel del Sitio',
                    'subtitle': 'Resumen operativo del sitio',
                    'site': 'Sitio', 'year': 'Ano', 'generated': 'Generado el',
                    'budget_section': 'Resumen Presupuesto',
                    'budget_headers': ['Categoria', 'Descripcion', 'Presupuestado', 'Real', 'Diferencia'],
                    'total': 'TOTAL', 'budgeted': 'Presupuestado', 'actual': 'Real',
                    'personnel_section': 'Personal',
                    'pers_headers': ['Nombre', 'Apellido', 'Rol', 'Contrato', 'Email', 'Tarifa Diaria'],
                    'equip_section': 'Inventario de Equipos',
                    'equip_headers': ['Codigo', 'Nombre', 'Categoria', 'Marca', 'Modelo', 'Estado'],
                    'statistics': 'Estadisticas',
                    'total_personnel': 'Total Personal',
                    'total_equipment': 'Total Equipos',
                    'budget_variance': 'Variacion Presupuesto',
                    'budget_chart': 'Presupuesto por Categoria',
                    'page': 'Pagina',
                    'footer': 'pyArchInit - Gestion de Datos Arqueologicos',
                    'no_data': 'Sin datos disponibles',
                },
                'fr': {
                    'title': 'Tableau de Bord du Chantier',
                    'subtitle': 'Resume operationnel du chantier',
                    'site': 'Chantier', 'year': 'Annee', 'generated': 'Genere le',
                    'budget_section': 'Resume du Budget',
                    'budget_headers': ['Categorie', 'Description', 'Prevu', 'Reel', 'Ecart'],
                    'total': 'TOTAL', 'budgeted': 'Prevu', 'actual': 'Reel',
                    'personnel_section': 'Personnel',
                    'pers_headers': ['Prenom', 'Nom', 'Role', 'Contrat', 'Email', 'Tarif Journalier'],
                    'equip_section': 'Inventaire des Equipements',
                    'equip_headers': ['Code', 'Nom', 'Categorie', 'Marque', 'Modele', 'Etat'],
                    'statistics': 'Statistiques',
                    'total_personnel': 'Total Personnel',
                    'total_equipment': 'Total Equipements',
                    'budget_variance': 'Ecart Budgetaire',
                    'budget_chart': 'Budget par Categorie',
                    'page': 'Page',
                    'footer': 'pyArchInit - Gestion des Donnees Archeologiques',
                    'no_data': 'Aucune donnee disponible',
                },
            }
            tr = i18n.get(lang, i18n['en'])

            # --- Styles ---
            styles = getSampleStyleSheet()
            style_title = ParagraphStyle('DashTitle', parent=styles['Title'],
                                         fontName='Helvetica-Bold', fontSize=22,
                                         textColor=CLR_HEADER, spaceAfter=1 * mm)
            style_subtitle = ParagraphStyle('DashSubtitle', parent=styles['Normal'],
                                            fontName='Helvetica', fontSize=11,
                                            textColor=colors.HexColor('#546e7a'), spaceAfter=1 * mm)
            style_section = ParagraphStyle('DashSection', parent=styles['Heading2'],
                                           fontName='Helvetica-Bold', fontSize=14,
                                           textColor=CLR_HEADER, spaceBefore=6 * mm, spaceAfter=3 * mm)
            style_cell = ParagraphStyle('DCell', fontName='Helvetica', fontSize=8,
                                        leading=10, alignment=TA_LEFT)
            style_cell_right = ParagraphStyle('DCellR', fontName='Helvetica', fontSize=8,
                                              leading=10, alignment=TA_RIGHT)
            style_cell_center = ParagraphStyle('DCellC', fontName='Helvetica', fontSize=8,
                                               leading=10, alignment=TA_CENTER)
            style_cell_bold = ParagraphStyle('DCellB', fontName='Helvetica-Bold', fontSize=8,
                                             leading=10, alignment=TA_LEFT)
            style_cell_bold_right = ParagraphStyle('DCellBR', fontName='Helvetica-Bold', fontSize=8,
                                                    leading=10, alignment=TA_RIGHT)
            style_header_cell = ParagraphStyle('DHdrCell', fontName='Helvetica-Bold', fontSize=8.5,
                                               leading=11, textColor=CLR_TEXT_LIGHT, alignment=TA_CENTER)
            style_stat_label = ParagraphStyle('StatLbl', fontName='Helvetica-Bold', fontSize=10,
                                              textColor=CLR_HEADER)
            style_stat_val = ParagraphStyle('StatVal', fontName='Helvetica-Bold', fontSize=12,
                                            textColor=colors.HexColor('#0d47a1'), alignment=TA_RIGHT)

            def make_table_style():
                """Return standard professional table style commands."""
                return [
                    ('BACKGROUND', (0, 0), (-1, 0), CLR_HEADER),
                    ('TEXTCOLOR', (0, 0), (-1, 0), CLR_TEXT_LIGHT),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 8.5),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 5),
                    ('TOPPADDING', (0, 0), (-1, 0), 5),
                    ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 1), (-1, -1), 8),
                    ('TOPPADDING', (0, 1), (-1, -1), 3),
                    ('BOTTOMPADDING', (0, 1), (-1, -1), 3),
                    ('LEFTPADDING', (0, 0), (-1, -1), 4),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 4),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, CLR_ROW_ALT]),
                    ('GRID', (0, 0), (-1, 0), 0.5, CLR_HEADER),
                    ('LINEBELOW', (0, 0), (-1, 0), 1.5, CLR_SECTION_LINE),
                    ('INNERGRID', (0, 1), (-1, -1), 0.25, CLR_BORDER),
                    ('BOX', (0, 0), (-1, -1), 0.75, CLR_HEADER),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ]

            # --- Header/Footer ---
            def header_footer(canvas, doc):
                canvas.saveState()

                # Header bar
                canvas.setFillColor(CLR_HEADER)
                canvas.rect(0, page_h - 16 * mm, page_w, 16 * mm, fill=1, stroke=0)
                canvas.setFillColor(CLR_SECTION_LINE)
                canvas.rect(0, page_h - 17 * mm, page_w, 1 * mm, fill=1, stroke=0)

                canvas.setFont('Helvetica-Bold', 13)
                canvas.setFillColor(CLR_TEXT_LIGHT)
                canvas.drawString(12 * mm, page_h - 11 * mm, "pyArchInit")

                canvas.setFont('Helvetica', 9)
                canvas.drawString(48 * mm, page_h - 11 * mm,
                                  f"|  {tr['site']}: {sito}  |  {tr['year']}: {anno}")

                gen_date = datetime.now().strftime('%Y-%m-%d %H:%M')
                canvas.drawRightString(page_w - 12 * mm, page_h - 11 * mm,
                                       f"{tr['generated']}: {gen_date}")

                # Footer
                canvas.setFillColor(CLR_HEADER)
                canvas.rect(0, 0, page_w, 10 * mm, fill=1, stroke=0)
                canvas.setFont('Helvetica', 7)
                canvas.setFillColor(CLR_TEXT_LIGHT)
                canvas.drawString(12 * mm, 3.5 * mm, tr['footer'])
                canvas.drawRightString(page_w - 12 * mm, 3.5 * mm,
                                       f"{tr['page']} {canvas.getPageNumber()}")
                canvas.restoreState()

            # --- Build document ---
            doc = SimpleDocTemplate(
                file_path, pagesize=A4,
                topMargin=22 * mm, bottomMargin=15 * mm,
                leftMargin=12 * mm, rightMargin=12 * mm,
            )
            usable_w = page_w - 24 * mm
            elements = []

            # ========== TITLE PAGE ==========
            elements.append(Spacer(1, 40 * mm))
            elements.append(Paragraph(tr['title'], ParagraphStyle(
                'BigTitle', fontName='Helvetica-Bold', fontSize=32,
                textColor=CLR_HEADER, alignment=TA_CENTER, spaceAfter=5 * mm)))
            elements.append(HRFlowable(width="60%", thickness=2, color=CLR_SECTION_LINE,
                                       spaceAfter=5 * mm, spaceBefore=2 * mm))
            elements.append(Paragraph(f"{tr['site']}: <b>{sito}</b>", ParagraphStyle(
                'TitleSite', fontName='Helvetica', fontSize=16,
                textColor=colors.HexColor('#37474f'), alignment=TA_CENTER, spaceAfter=3 * mm)))
            elements.append(Paragraph(f"{tr['year']}: <b>{anno}</b>", ParagraphStyle(
                'TitleYear', fontName='Helvetica', fontSize=14,
                textColor=colors.HexColor('#546e7a'), alignment=TA_CENTER, spaceAfter=8 * mm)))
            elements.append(Paragraph(tr['subtitle'], ParagraphStyle(
                'TitleSub', fontName='Helvetica-Oblique', fontSize=11,
                textColor=colors.HexColor('#78909c'), alignment=TA_CENTER, spaceAfter=5 * mm)))

            gen_date = datetime.now().strftime('%Y-%m-%d %H:%M')
            elements.append(Spacer(1, 20 * mm))
            elements.append(Paragraph(f"{tr['generated']}: {gen_date}", ParagraphStyle(
                'TitleDate', fontName='Helvetica', fontSize=10,
                textColor=colors.HexColor('#90a4ae'), alignment=TA_CENTER)))

            elements.append(PageBreak())

            # ========== BUDGET SECTION ==========
            budget_recs = []
            tot_prev = 0.0
            tot_eff = 0.0
            try:
                search_dict = {'sito': "'" + sito + "'"}
                if anno:
                    search_dict['anno'] = anno
                budget_recs = self.DB_MANAGER.query_bool(search_dict, 'BUDGET')
                tot_prev = sum(float(r.importo_previsto or 0) for r in budget_recs)
                tot_eff = sum(float(r.importo_effettivo or 0) for r in budget_recs)
            except Exception:
                pass

            elements.append(Paragraph(tr['budget_section'], style_section))

            if budget_recs:
                # Budget table
                bhdrs = tr['budget_headers']
                bheader_row = [Paragraph(h, style_header_cell) for h in bhdrs]
                bdata = [bheader_row]
                for r in budget_recs:
                    prev = float(r.importo_previsto or 0)
                    eff = float(r.importo_effettivo or 0)
                    diff = prev - eff
                    diff_color = '#2e7d32' if diff >= 0 else '#c62828'
                    bdata.append([
                        Paragraph(str(r.categoria or ''), style_cell),
                        Paragraph(str(r.descrizione or ''), style_cell),
                        Paragraph(f"\u20ac {prev:,.2f}", style_cell_right),
                        Paragraph(f"\u20ac {eff:,.2f}", style_cell_right),
                        Paragraph(f'<font color="{diff_color}">\u20ac {diff:,.2f}</font>', style_cell_right),
                    ])
                # Total row
                total_diff = tot_prev - tot_eff
                diff_color = '#2e7d32' if total_diff >= 0 else '#c62828'
                bdata.append([
                    Paragraph(f"<b>{tr['total']}</b>", style_cell_bold),
                    Paragraph('', style_cell),
                    Paragraph(f"<b>\u20ac {tot_prev:,.2f}</b>", style_cell_bold_right),
                    Paragraph(f"<b>\u20ac {tot_eff:,.2f}</b>", style_cell_bold_right),
                    Paragraph(f'<b><font color="{diff_color}">\u20ac {total_diff:,.2f}</font></b>', style_cell_bold_right),
                ])

                bcol_widths = [30 * mm, 55 * mm, 30 * mm, 30 * mm, 28 * mm]
                btbl = Table(bdata, colWidths=bcol_widths, repeatRows=1)
                ts = make_table_style()
                ts.extend([
                    ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#c5cae9')),
                    ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
                ])
                btbl.setStyle(TableStyle(ts))
                elements.append(btbl)

                # ========== BUDGET BAR CHART ==========
                elements.append(Spacer(1, 5 * mm))
                elements.append(Paragraph(tr['budget_chart'], ParagraphStyle(
                    'ChartTitle', fontName='Helvetica-Bold', fontSize=11,
                    textColor=CLR_HEADER, spaceBefore=3 * mm, spaceAfter=3 * mm)))

                # Build bar chart using ReportLab Drawing
                categories = []
                budgeted_vals = []
                actual_vals = []
                for r in budget_recs:
                    cat_name = str(r.categoria or '?')
                    if len(cat_name) > 15:
                        cat_name = cat_name[:14] + '..'
                    categories.append(cat_name)
                    budgeted_vals.append(float(r.importo_previsto or 0))
                    actual_vals.append(float(r.importo_effettivo or 0))

                num_cats = len(categories)
                if num_cats > 0:
                    chart_w = float(usable_w)
                    bar_area_w = chart_w - 25 * mm  # leave space for labels
                    chart_h = max(80, num_cats * 22 + 40)
                    drawing = Drawing(chart_w, chart_h)

                    max_val = max(max(budgeted_vals, default=1), max(actual_vals, default=1), 1)
                    bar_height = 7
                    group_spacing = 22
                    x_offset = 25 * mm
                    y_start = chart_h - 25

                    # Legend
                    drawing.add(Rect(x_offset, chart_h - 12, 10, 6,
                                     fillColor=CLR_BUDGET, strokeColor=None))
                    drawing.add(String(x_offset + 13, chart_h - 11,
                                       tr['budgeted'], fontName='Helvetica', fontSize=7,
                                       fillColor=colors.HexColor('#333333')))
                    drawing.add(Rect(x_offset + 55, chart_h - 12, 10, 6,
                                     fillColor=CLR_ACTUAL, strokeColor=None))
                    drawing.add(String(x_offset + 68, chart_h - 11,
                                       tr['actual'], fontName='Helvetica', fontSize=7,
                                       fillColor=colors.HexColor('#333333')))

                    for i, cat in enumerate(categories):
                        y_pos = y_start - i * group_spacing

                        # Category label
                        drawing.add(String(2, y_pos - 1, cat,
                                           fontName='Helvetica', fontSize=7,
                                           fillColor=colors.HexColor('#333333')))

                        # Budgeted bar
                        bw = (budgeted_vals[i] / max_val) * float(bar_area_w) if max_val else 0
                        drawing.add(Rect(x_offset, y_pos, max(bw, 1), bar_height,
                                         fillColor=CLR_BUDGET, strokeColor=None))
                        if bw > 2:
                            drawing.add(String(x_offset + bw + 2, y_pos + 1,
                                               f"\u20ac{budgeted_vals[i]:,.0f}",
                                               fontName='Helvetica', fontSize=6,
                                               fillColor=CLR_BUDGET))

                        # Actual bar
                        aw = (actual_vals[i] / max_val) * float(bar_area_w) if max_val else 0
                        drawing.add(Rect(x_offset, y_pos - bar_height - 1, max(aw, 1), bar_height,
                                         fillColor=CLR_ACTUAL, strokeColor=None))
                        if aw > 2:
                            drawing.add(String(x_offset + aw + 2, y_pos - bar_height,
                                               f"\u20ac{actual_vals[i]:,.0f}",
                                               fontName='Helvetica', fontSize=6,
                                               fillColor=CLR_ACTUAL))

                    elements.append(drawing)
            else:
                elements.append(Paragraph(f"<i>{tr['no_data']}</i>", style_cell))

            elements.append(Spacer(1, 4 * mm))
            elements.append(HRFlowable(width="100%", thickness=0.5, color=CLR_BORDER,
                                       spaceAfter=2 * mm))

            # ========== PERSONNEL SECTION ==========
            pers_recs = []
            try:
                search_dict = {'sito': "'" + sito + "'"}
                pers_recs = self.DB_MANAGER.query_bool(search_dict, 'PERSONALE')
            except Exception:
                pass

            elements.append(Paragraph(tr['personnel_section'], style_section))
            if pers_recs:
                phdrs = tr['pers_headers']
                pheader_row = [Paragraph(h, style_header_cell) for h in phdrs]
                pdata = [pheader_row]
                for r in pers_recs:
                    rate_str = ''
                    try:
                        if r.tariffa_giornaliera:
                            rate_str = f"\u20ac {float(r.tariffa_giornaliera):,.2f}"
                    except (ValueError, TypeError):
                        rate_str = str(r.tariffa_giornaliera) if r.tariffa_giornaliera else ''
                    pdata.append([
                        Paragraph(str(r.nome or ''), style_cell),
                        Paragraph(str(r.cognome or ''), style_cell),
                        Paragraph(str(r.ruolo or ''), style_cell_center),
                        Paragraph(str(r.tipo_contratto or ''), style_cell_center),
                        Paragraph(str(r.email or ''), style_cell),
                        Paragraph(rate_str, style_cell_right),
                    ])

                pcol_widths = [28 * mm, 32 * mm, 32 * mm, 28 * mm, 40 * mm, 22 * mm]
                ptbl = Table(pdata, colWidths=pcol_widths, repeatRows=1)
                ptbl.setStyle(TableStyle(make_table_style()))
                elements.append(ptbl)
            else:
                elements.append(Paragraph(f"<i>{tr['no_data']}</i>", style_cell))

            elements.append(Spacer(1, 4 * mm))
            elements.append(HRFlowable(width="100%", thickness=0.5, color=CLR_BORDER,
                                       spaceAfter=2 * mm))

            # ========== EQUIPMENT SECTION ==========
            equip_recs = []
            try:
                search_dict = {'sito': "'" + sito + "'"}
                equip_recs = self.DB_MANAGER.query_bool(search_dict, 'ATTREZZATURE')
            except Exception:
                pass

            elements.append(Paragraph(tr['equip_section'], style_section))
            if equip_recs:
                ehdrs = tr['equip_headers']
                eheader_row = [Paragraph(h, style_header_cell) for h in ehdrs]
                edata = [eheader_row]
                for r in equip_recs:
                    # Color-code status
                    status_str = str(r.stato or '')
                    status_lower = status_str.lower()
                    if status_lower in ('in uso', 'in use', 'im einsatz', 'en uso', 'en utilisation'):
                        status_str = f'<font color="#2e7d32">{status_str}</font>'
                    elif status_lower in ('manutenzione', 'maintenance', 'wartung', 'mantenimiento', 'entretien'):
                        status_str = f'<font color="#e65100">{status_str}</font>'
                    elif status_lower in ('dismesso', 'decommissioned', 'ausgemustert', 'dado de baja', 'hors service'):
                        status_str = f'<font color="#c62828">{status_str}</font>'

                    edata.append([
                        Paragraph(str(r.codice_inventario or ''), style_cell_center),
                        Paragraph(str(r.nome or ''), style_cell),
                        Paragraph(str(r.categoria or ''), style_cell_center),
                        Paragraph(str(r.marca or ''), style_cell),
                        Paragraph(str(r.modello or ''), style_cell),
                        Paragraph(status_str, style_cell_center),
                    ])

                ecol_widths = [25 * mm, 38 * mm, 30 * mm, 28 * mm, 30 * mm, 28 * mm]
                etbl = Table(edata, colWidths=ecol_widths, repeatRows=1)
                etbl.setStyle(TableStyle(make_table_style()))
                elements.append(etbl)
            else:
                elements.append(Paragraph(f"<i>{tr['no_data']}</i>", style_cell))

            # ========== SUMMARY STATISTICS ==========
            elements.append(Spacer(1, 6 * mm))
            elements.append(Paragraph(tr['statistics'], style_section))

            variance = tot_prev - tot_eff
            var_color = '#2e7d32' if variance >= 0 else '#c62828'

            stat_data = [
                [Paragraph(tr['total_personnel'], style_stat_label),
                 Paragraph(str(len(pers_recs)), style_stat_val),
                 Paragraph(tr['total_equipment'], style_stat_label),
                 Paragraph(str(len(equip_recs)), style_stat_val)],
                [Paragraph(tr['budget_headers'][2], style_stat_label),
                 Paragraph(f"\u20ac {tot_prev:,.2f}", style_stat_val),
                 Paragraph(tr['budget_headers'][3], style_stat_label),
                 Paragraph(f"\u20ac {tot_eff:,.2f}", style_stat_val)],
                [Paragraph(tr['budget_variance'], style_stat_label),
                 Paragraph(f'<font color="{var_color}">\u20ac {variance:,.2f}</font>',
                           ParagraphStyle('VarVal', fontName='Helvetica-Bold', fontSize=12,
                                          textColor=colors.HexColor(var_color), alignment=TA_RIGHT)),
                 Paragraph('', style_stat_label),
                 Paragraph('', style_stat_val)],
            ]

            stat_col_widths = [42 * mm, 35 * mm, 42 * mm, 35 * mm]
            stat_tbl = Table(stat_data, colWidths=stat_col_widths)
            stat_tbl.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), CLR_SUMMARY_BG),
                ('BOX', (0, 0), (-1, -1), 1, CLR_HEADER),
                ('INNERGRID', (0, 0), (-1, -1), 0.5, CLR_BORDER),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('LEFTPADDING', (0, 0), (-1, -1), 6),
                ('RIGHTPADDING', (0, 0), (-1, -1), 6),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('BACKGROUND', (0, -1), (1, -1), colors.HexColor('#c5cae9')),
            ]))
            elements.append(stat_tbl)

            # Build with header/footer
            doc.build(elements, onFirstPage=header_footer, onLaterPages=header_footer)

            QMessageBox.information(self, "OK", f"PDF exported: {file_path}", QMessageBox.StandardButton.Ok)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"PDF export failed: {str(e)}", QMessageBox.StandardButton.Ok)

    def on_pushButton_export_excel_pressed(self):
        """Export dashboard data to CSV/Excel."""
        sito = self.comboBox_sito.currentText()
        anno = self.comboBox_anno.currentText()
        if not sito:
            QMessageBox.warning(self, "Warning", "Select a site first.", QMessageBox.StandardButton.Ok)
            return

        home = os.environ.get('PYARCHINIT_HOME', os.path.expanduser('~'))
        file_path, _ = QFileDialog.getSaveFileName(self, "Export CSV", os.path.join(home, f"site_dashboard_{sito}_{anno}.csv"), "CSV (*.csv)")
        if not file_path:
            return

        try:
            import csv
            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)

                # Budget section
                writer.writerow(['=== BUDGET ==='])
                writer.writerow(['Category', 'Description', 'Budgeted', 'Actual', 'Supplier', 'Invoice', 'Date'])
                try:
                    search_dict = {'sito': "'" + sito + "'"}
                    if anno:
                        search_dict['anno'] = anno
                    for r in self.DB_MANAGER.query_bool(search_dict, 'BUDGET'):
                        writer.writerow([r.categoria, r.descrizione, r.importo_previsto, r.importo_effettivo, r.fornitore, r.numero_fattura, r.data_spesa])
                except Exception:
                    pass

                writer.writerow([])
                writer.writerow(['=== PERSONNEL ==='])
                writer.writerow(['Name', 'Surname', 'Role', 'Email', 'Phone', 'Contract', 'Daily Rate'])
                try:
                    search_dict = {'sito': "'" + sito + "'"}
                    for r in self.DB_MANAGER.query_bool(search_dict, 'PERSONALE'):
                        writer.writerow([r.nome, r.cognome, r.ruolo, r.email, r.telefono, r.tipo_contratto, r.tariffa_giornaliera])
                except Exception:
                    pass

                writer.writerow([])
                writer.writerow(['=== EQUIPMENT ==='])
                writer.writerow(['Code', 'Name', 'Category', 'Brand', 'Model', 'Status', 'Ownership'])
                try:
                    search_dict = {'sito': "'" + sito + "'"}
                    for r in self.DB_MANAGER.query_bool(search_dict, 'ATTREZZATURE'):
                        writer.writerow([r.codice_inventario, r.nome, r.categoria, r.marca, r.modello, r.stato, r.proprieta])
                except Exception:
                    pass

            QMessageBox.information(self, "OK", f"Export completed: {file_path}", QMessageBox.StandardButton.Ok)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Export failed: {str(e)}", QMessageBox.StandardButton.Ok)


## Class end

if __name__ == "__main__":
    from qgis.PyQt.QtWidgets import QApplication
    import sys
    app = QApplication(sys.argv)
    ui = pyarchinit_Cantiere(None)
    ui.show()
    sys.exit(app.exec())
