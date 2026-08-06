#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dialog "Importa da QField" — GUI sopra modules.utility.qfield_importer.

Anteprima (dry-run) e Importa girano nello stesso worker QThread: QGIS non
si blocca durante la copia foto/WebDAV. DB risolto dal config del plugin
(pattern rapporti_check_dialog): nessun campo URL in interfaccia.
"""

import os

from qgis.PyQt.QtCore import QThread, pyqtSignal
from qgis.PyQt.QtWidgets import (
    QCheckBox, QDialog, QFileDialog, QGridLayout, QGroupBox, QHBoxLayout,
    QLabel, QLineEdit, QComboBox, QMessageBox, QProgressBar, QPushButton,
    QTextEdit, QVBoxLayout)
from qgis.core import QgsSettings

TRANSLATIONS = {
    'window_title': {
        'it': "Importa da QField - PyArchInit",
        'en': "Import from QField - PyArchInit",
        'de': "Aus QField importieren - PyArchInit",
        'es': "Importar desde QField - PyArchInit",
        'fr': "Importer depuis QField - PyArchInit",
        'ar': "استيراد من QField - PyArchInit",
        'ca': "Importa des de QField - PyArchInit",
        'ro': "Import din QField - PyArchInit",
        'pt': "Importar do QField - PyArchInit",
        'el': "Εισαγωγή από QField - PyArchInit",
    },
    'qfield_dir': {
        'it': "Cartella progetto QField:", 'en': "QField project folder:",
        'de': "QField-Projektordner:", 'es': "Carpeta del proyecto QField:",
        'fr': "Dossier du projet QField :", 'ar': "مجلد مشروع QField:",
        'ca': "Carpeta del projecte QField:", 'ro': "Folder proiect QField:",
        'pt': "Pasta do projeto QField:", 'el': "Φάκελος έργου QField:",
    },
    'browse': {
        'it': "Sfoglia…", 'en': "Browse…", 'de': "Durchsuchen…",
        'es': "Examinar…", 'fr': "Parcourir…", 'ar': "تصفح…",
        'ca': "Navega…", 'ro': "Răsfoiește…", 'pt': "Procurar…",
        'el': "Αναζήτηση…",
    },
    'zip_browse': {
        'it': "Archivio ZIP…", 'en': "ZIP archive…", 'de': "ZIP-Archiv…",
        'es': "Archivo ZIP…", 'fr': "Archive ZIP…", 'ar': "أرشيف ZIP…",
        'ca': "Arxiu ZIP…", 'ro': "Arhivă ZIP…", 'pt': "Arquivo ZIP…",
        'el': "Αρχείο ZIP…",
    },
    'zip_filter': {
        'it': "Archivi ZIP (*.zip)", 'en': "ZIP archives (*.zip)",
        'de': "ZIP-Archive (*.zip)", 'es': "Archivos ZIP (*.zip)",
        'fr': "Archives ZIP (*.zip)", 'ar': "أرشيفات ZIP (*.zip)",
        'ca': "Arxius ZIP (*.zip)", 'ro': "Arhive ZIP (*.zip)",
        'pt': "Arquivos ZIP (*.zip)", 'el': "Αρχεία ZIP (*.zip)",
    },
    'site': {
        'it': "Sito:", 'en': "Site:", 'de': "Fundort:", 'es': "Sitio:",
        'fr': "Site :", 'ar': "الموقع:", 'ca': "Jaciment:", 'ro': "Sit:",
        'pt': "Sítio:", 'el': "Θέση:",
    },
    'all_sites': {
        'it': "Tutti i siti", 'en': "All sites", 'de': "Alle Fundorte",
        'es': "Todos los sitios", 'fr': "Tous les sites",
        'ar': "كل المواقع", 'ca': "Tots els jaciments",
        'ro': "Toate siturile", 'pt': "Todos os sítios",
        'el': "Όλες οι θέσεις",
    },
    'srid': {
        'it': "SRID (vuoto = dal GPKG):", 'en': "SRID (empty = from GPKG):",
        'de': "SRID (leer = aus GPKG):", 'es': "SRID (vacío = del GPKG):",
        'fr': "SRID (vide = du GPKG) :", 'ar': "SRID (فارغ = من GPKG):",
        'ca': "SRID (buit = del GPKG):", 'ro': "SRID (gol = din GPKG):",
        'pt': "SRID (vazio = do GPKG):", 'el': "SRID (κενό = από GPKG):",
    },
    'media_dest': {
        'it': "Destinazione foto:", 'en': "Photo destination:",
        'de': "Foto-Ziel:", 'es': "Destino de fotos:",
        'fr': "Destination des photos :", 'ar': "وجهة الصور:",
        'ca': "Destinació de fotos:", 'ro': "Destinație foto:",
        'pt': "Destino das fotos:", 'el': "Προορισμός φωτογραφιών:",
    },
    'opt_geom_dedup': {
        'it': "Deduplica geometrie", 'en': "Deduplicate geometries",
        'de': "Geometrien deduplizieren", 'es': "Deduplicar geometrías",
        'fr': "Dédupliquer les géométries", 'ar': "إزالة تكرار الأشكال",
        'ca': "Dedueix geometries", 'ro': "Deduplică geometriile",
        'pt': "Desduplicar geometrias", 'el': "Αφαίρεση διπλών γεωμετριών",
    },
    'opt_copy_media': {
        'it': "Copia foto", 'en': "Copy photos", 'de': "Fotos kopieren",
        'es': "Copiar fotos", 'fr': "Copier les photos", 'ar': "نسخ الصور",
        'ca': "Copia fotos", 'ro': "Copiază fotografiile",
        'pt': "Copiar fotos", 'el': "Αντιγραφή φωτογραφιών",
    },
    'opt_thumbs': {
        'it': "Genera thumbnail", 'en': "Generate thumbnails",
        'de': "Thumbnails erzeugen", 'es': "Generar miniaturas",
        'fr': "Générer les vignettes", 'ar': "إنشاء مصغرات",
        'ca': "Genera miniatures", 'ro': "Generează miniaturi",
        'pt': "Gerar miniaturas", 'el': "Δημιουργία μικρογραφιών",
    },
    'preview': {
        'it': "Anteprima (dry-run)", 'en': "Preview (dry-run)",
        'de': "Vorschau (Testlauf)", 'es': "Vista previa (simulación)",
        'fr': "Aperçu (simulation)", 'ar': "معاينة (تجريبي)",
        'ca': "Previsualització (simulació)", 'ro': "Previzualizare (test)",
        'pt': "Pré-visualização (simulação)", 'el': "Προεπισκόπηση (δοκιμή)",
    },
    'import_btn': {
        'it': "Importa", 'en': "Import", 'de': "Importieren",
        'es': "Importar", 'fr': "Importer", 'ar': "استيراد",
        'ca': "Importa", 'ro': "Importă", 'pt': "Importar",
        'el': "Εισαγωγή",
    },
    'close': {
        'it': "Chiudi", 'en': "Close", 'de': "Schließen", 'es': "Cerrar",
        'fr': "Fermer", 'ar': "إغلاق", 'ca': "Tanca", 'ro': "Închide",
        'pt': "Fechar", 'el': "Κλείσιμο",
    },
    'confirm_import': {
        'it': "Confermi l'import nel database corrente? L'operazione "
              "aggiunge record e riempie i campi vuoti delle schede "
              "esistenti (mai sovrascrive valori).",
        'en': "Confirm import into the current database? The operation "
              "appends records and fills empty fields of existing sheets "
              "(never overwrites values).",
        'de': "Import in die aktuelle Datenbank bestätigen? Es werden "
              "Datensätze angehängt und leere Felder gefüllt (nie "
              "überschrieben).",
        'es': "¿Confirmar la importación en la base de datos actual? "
              "Añade registros y rellena campos vacíos (nunca sobrescribe).",
        'fr': "Confirmer l'import dans la base actuelle ? Ajoute des "
              "enregistrements et remplit les champs vides (jamais "
              "d'écrasement).",
        'ar': "تأكيد الاستيراد إلى قاعدة البيانات الحالية؟ تضاف السجلات "
              "وتملأ الحقول الفارغة فقط (لا استبدال).",
        'ca': "Confirmes la importació a la base de dades actual? Afegeix "
              "registres i omple camps buits (mai sobreescriu).",
        'ro': "Confirmi importul în baza de date curentă? Adaugă "
              "înregistrări și completează câmpurile goale (nu suprascrie).",
        'pt': "Confirmar a importação na base de dados atual? Acrescenta "
              "registos e preenche campos vazios (nunca sobrescreve).",
        'el': "Επιβεβαίωση εισαγωγής στην τρέχουσα βάση; Προσθέτει "
              "εγγραφές και συμπληρώνει κενά πεδία (ποτέ αντικατάσταση).",
    },
    'error': {
        'it': "Errore", 'en': "Error", 'de': "Fehler", 'es': "Error",
        'fr': "Erreur", 'ar': "خطأ", 'ca': "Error", 'ro': "Eroare",
        'pt': "Erro", 'el': "Σφάλμα",
    },
    'done': {
        'it': "Import completato", 'en': "Import complete",
        'de': "Import abgeschlossen", 'es': "Importación completada",
        'fr': "Import terminé", 'ar': "اكتمل الاستيراد",
        'ca': "Importació completada", 'ro': "Import finalizat",
        'pt': "Importação concluída", 'el': "Η εισαγωγή ολοκληρώθηκε",
    },
    'choose_dir_first': {
        'it': "Scegli prima la cartella del progetto QField.",
        'en': "Choose the QField project folder first.",
        'de': "Wähle zuerst den QField-Projektordner.",
        'es': "Elige primero la carpeta del proyecto QField.",
        'fr': "Choisissez d'abord le dossier du projet QField.",
        'ar': "اختر مجلد مشروع QField أولاً.",
        'ca': "Tria primer la carpeta del projecte QField.",
        'ro': "Alege mai întâi folderul proiectului QField.",
        'pt': "Escolha primeiro a pasta do projeto QField.",
        'el': "Επιλέξτε πρώτα τον φάκελο του έργου QField.",
    },
    'srid_invalid': {
        'it': "SRID non valido: inserisci un numero intero (es. 32633) "
              "o lascia vuoto.",
        'en': "Invalid SRID: enter an integer (e.g. 32633) or leave "
              "empty.",
        'de': "Ungültige SRID: Gib eine Ganzzahl ein (z. B. 32633) "
              "oder lasse das Feld leer.",
        'es': "SRID no válido: introduce un número entero (p. ej. "
              "32633) o déjalo vacío.",
        'fr': "SRID non valide : saisissez un nombre entier "
              "(ex. 32633) ou laissez vide.",
        'ar': "SRID غير صالح: أدخل رقمًا صحيحًا (مثل 32633) أو اتركه "
              "فارغًا.",
        'ca': "SRID no vàlid: introdueix un nombre enter (p. ex. "
              "32633) o deixa'l buit.",
        'ro': "SRID invalid: introdu un număr întreg (ex. 32633) sau "
              "lasă gol.",
        'pt': "SRID inválido: insira um número inteiro (ex. 32633) "
              "ou deixe vazio.",
        'el': "Μη έγκυρο SRID: εισαγάγετε έναν ακέραιο αριθμό (π.χ. "
              "32633) ή αφήστε το κενό.",
    },
}


def _lang():
    code = QgsSettings().value("locale/userLocale", "it", type=str)[:2]
    return code if code in ('it', 'en', 'de', 'es', 'fr',
                            'ar', 'ca', 'ro', 'pt', 'el') else 'en'


class QFieldImportWorker(QThread):
    """Esegue scan/anteprima/import fuori dal main thread."""
    log_message = pyqtSignal(str)
    finished_ok = pyqtSignal(object)   # QFieldImportResult
    failed = pyqtSignal(str)

    def __init__(self, db_manager, params, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.params = params

    def run(self):
        try:
            from ..modules.utility.qfield_importer import run_qfield_import
        except ImportError:
            from modules.utility.qfield_importer import run_qfield_import
        try:
            result = run_qfield_import(
                self.db_manager, self.params["qfield_dir"],
                sito=self.params["sito"], srid=self.params["srid"],
                dry_run=self.params["dry_run"],
                geom_dedup=self.params["geom_dedup"],
                copy_media=self.params["copy_media"],
                make_thumbs=self.params["make_thumbs"],
                media_dest=self.params["media_dest"],
                thumb_path=self.params["thumb_path"],
                thumb_resize=self.params["thumb_resize"],
                log=self.log_message.emit)
            self.finished_ok.emit(result)
        except Exception as e:
            self.failed.emit(str(e))


class QFieldImportDialog(QDialog):
    """Importa da QField. db_manager opzionale: se assente si auto-risolve
    dal config del plugin (pattern rapporti_check_dialog)."""

    def __init__(self, db_manager=None, parent=None):
        super().__init__(parent)
        self.L = _lang()
        self.worker = None
        self._thumb_path = ""
        self._thumb_resize = ""
        self.db_manager = db_manager or self._resolve_db()
        self.setWindowTitle(self.tr_('window_title'))
        self.resize(760, 620)
        self._build_ui()

    def tr_(self, key):
        entry = TRANSLATIONS.get(key, {})
        return entry.get(self.L, entry.get('en', key))

    # -- setup -------------------------------------------------------------

    def _resolve_db(self):
        try:
            from ..modules.db.pyarchinit_conn_strings import Connection
            from ..modules.db.pyarchinit_db_manager import get_db_manager
        except ImportError:
            from modules.db.pyarchinit_conn_strings import Connection
            from modules.db.pyarchinit_db_manager import get_db_manager
        conn = Connection()
        self._thumb_path = conn.thumb_path().get("thumb_path", "")
        self._thumb_resize = conn.thumb_resize().get("thumb_resize", "")
        return get_db_manager(conn.conn_str(), use_singleton=True)

    def _build_ui(self):
        try:
            from ..modules.utility.qfield_importer import default_media_dest
        except ImportError:
            from modules.utility.qfield_importer import default_media_dest

        layout = QVBoxLayout(self)

        grid = QGridLayout()
        grid.addWidget(QLabel(self.tr_('qfield_dir')), 0, 0)
        self.dir_edit = QLineEdit()
        grid.addWidget(self.dir_edit, 0, 1)
        self.browse_btn = QPushButton(self.tr_('browse'))
        self.browse_btn.clicked.connect(self._choose_dir)
        grid.addWidget(self.browse_btn, 0, 2)
        self.zip_btn = QPushButton(self.tr_('zip_browse'))
        self.zip_btn.clicked.connect(self._choose_zip)
        grid.addWidget(self.zip_btn, 0, 3)

        grid.addWidget(QLabel(self.tr_('site')), 1, 0)
        self.site_combo = QComboBox()
        self.site_combo.addItem(self.tr_('all_sites'), None)
        grid.addWidget(self.site_combo, 1, 1)

        grid.addWidget(QLabel(self.tr_('srid')), 2, 0)
        self.srid_edit = QLineEdit()
        grid.addWidget(self.srid_edit, 2, 1)

        grid.addWidget(QLabel(self.tr_('media_dest')), 3, 0)
        self.media_dest_edit = QLineEdit(
            default_media_dest(self._thumb_path))
        grid.addWidget(self.media_dest_edit, 3, 1)
        layout.addLayout(grid)

        opts = QGroupBox()
        opts_layout = QHBoxLayout(opts)
        self.geom_dedup_check = QCheckBox(self.tr_('opt_geom_dedup'))
        self.geom_dedup_check.setChecked(True)
        self.copy_media_check = QCheckBox(self.tr_('opt_copy_media'))
        self.copy_media_check.setChecked(True)
        self.thumbs_check = QCheckBox(self.tr_('opt_thumbs'))
        self.thumbs_check.setChecked(True)
        # Le thumbnail leggono il file gia' copiato nel backend media: senza
        # copia i filepath restano relativi al progetto QField e ogni
        # thumbnail fallirebbe. Legano quindi "Genera thumbnail" alla copia.
        self.copy_media_check.toggled.connect(self._on_copy_media_toggled)
        for w in (self.geom_dedup_check, self.copy_media_check,
                  self.thumbs_check):
            opts_layout.addWidget(w)
        layout.addWidget(opts)

        self.log_view = QTextEdit()
        self.log_view.setReadOnly(True)
        layout.addWidget(self.log_view, stretch=1)

        self.progress = QProgressBar()
        self.progress.setRange(0, 0)
        self.progress.hide()
        layout.addWidget(self.progress)

        buttons = QHBoxLayout()
        self.preview_btn = QPushButton(self.tr_('preview'))
        self.preview_btn.clicked.connect(lambda: self._start(dry_run=True))
        self.import_btn = QPushButton(self.tr_('import_btn'))
        self.import_btn.clicked.connect(lambda: self._start(dry_run=False))
        self.close_btn = QPushButton(self.tr_('close'))
        self.close_btn.clicked.connect(self.close)
        buttons.addWidget(self.preview_btn)
        buttons.addWidget(self.import_btn)
        buttons.addStretch()
        buttons.addWidget(self.close_btn)
        layout.addLayout(buttons)

    # -- interazioni ---------------------------------------------------------

    def _choose_dir(self):
        directory = QFileDialog.getExistingDirectory(
            self, self.tr_('qfield_dir'), os.path.expanduser("~"))
        if not directory:
            return
        self.dir_edit.setText(directory)
        self._scan_sites(directory)

    def _choose_zip(self):
        path, _ = QFileDialog.getOpenFileName(
            self, self.tr_('zip_browse'), os.path.expanduser("~"),
            self.tr_('zip_filter'))
        if not path:
            return
        self.dir_edit.setText(path)
        # niente scansione siti dal .zip (servirebbe estrarlo nel main
        # thread): la combo torna a "Tutti i siti"
        self.site_combo.clear()
        self.site_combo.addItem(self.tr_('all_sites'), None)

    def _scan_sites(self, directory):
        """Popola la combo siti dai GPKG (scan veloce, main thread ok)."""
        try:
            from ..modules.utility.qfield_importer import (
                find_gpkg_layers, read_features, sito_field_for)
        except ImportError:
            from modules.utility.qfield_importer import (
                find_gpkg_layers, read_features, sito_field_for)
        self.site_combo.clear()
        self.site_combo.addItem(self.tr_('all_sites'), None)
        try:
            layers = find_gpkg_layers(directory)
            self.log_view.append("Layer trovati:")
            sites = set()
            for name, (path, layer_name) in layers.items():
                self.log_view.append(f"  {name}: {os.path.basename(path)}")
                if name == "us_table":
                    f = sito_field_for(name)
                    for r in read_features(path, layer_name):
                        v = r.get(f)
                        if v:
                            sites.add(str(v).strip())
            for s in sorted(sites):
                self.site_combo.addItem(s, s)
        except Exception as e:
            self.log_view.append(f"Scan fallito: {e}")

    def _params(self, dry_run):
        srid_text = self.srid_edit.text().strip()
        return {
            "qfield_dir": self.dir_edit.text().strip(),
            "sito": self.site_combo.currentData(),
            "srid": int(srid_text) if srid_text else None,
            "dry_run": dry_run,
            "geom_dedup": self.geom_dedup_check.isChecked(),
            "copy_media": self.copy_media_check.isChecked(),
            "make_thumbs": self.thumbs_check.isChecked(),
            "media_dest": self.media_dest_edit.text().strip() or None,
            "thumb_path": self._thumb_path,
            "thumb_resize": self._thumb_resize,
        }

    def _start(self, dry_run):
        if self.worker is not None and self.worker.isRunning():
            return
        if not self.dir_edit.text().strip():
            QMessageBox.warning(self, self.tr_('error'),
                                self.tr_('choose_dir_first'))
            return
        if not dry_run:
            reply = QMessageBox.question(
                self, self.tr_('import_btn'), self.tr_('confirm_import'),
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply != QMessageBox.StandardButton.Yes:
                return
        try:
            params = self._params(dry_run)
        except ValueError:
            QMessageBox.warning(self, self.tr_('error'),
                                self.tr_('srid_invalid'))
            return
        self.log_view.clear()
        self._set_running(True)
        self.worker = QFieldImportWorker(self.db_manager, params, self)
        self.worker.log_message.connect(self.log_view.append)
        self.worker.finished_ok.connect(self._on_done)
        self.worker.failed.connect(self._on_failed)
        self.worker.start()

    def _on_copy_media_toggled(self, checked):
        """Senza copia foto le thumbnail non hanno un file leggibile: la
        checkbox 'Genera thumbnail' viene disattivata (e deselezionata)
        quando 'Copia foto' e' spenta, riattivata quando si riaccende."""
        self.thumbs_check.setEnabled(checked)
        if not checked:
            self.thumbs_check.setChecked(False)

    def _set_running(self, running):
        for w in (self.preview_btn, self.import_btn, self.browse_btn,
                  self.zip_btn, self.close_btn, self.dir_edit, self.site_combo,
                  self.srid_edit, self.media_dest_edit,
                  self.geom_dedup_check, self.copy_media_check,
                  self.thumbs_check):
            w.setEnabled(not running)
        self.progress.setVisible(running)
        # Ripristina il vincolo thumbnail↔copia dopo il lockout del run.
        if not running:
            self.thumbs_check.setEnabled(self.copy_media_check.isChecked())

    def closeEvent(self, event):
        if self.worker is not None and self.worker.isRunning():
            self.log_view.append(
                "Import in corso: chiudi dopo il completamento."
                if self.L == 'it' else
                "Import running: close after it finishes.")
            event.ignore()
            return
        super().closeEvent(event)

    def _on_done(self, result):
        self._set_running(False)
        if not result.dry_run:
            QMessageBox.information(self, self.tr_('done'),
                                    "\n".join(result.summary_lines()))

    def _on_failed(self, message):
        self._set_running(False)
        QMessageBox.critical(self, self.tr_('error'), message)
