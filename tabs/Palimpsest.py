# -*- coding: utf-8 -*-
"""
Palimpsest Analysis Dialog for pyArchInit.

Runs the palimpsestr Stratigraphic Entanglement Field (SEF) analysis directly
on the currently connected pyArchInit SQLite/Spatialite database, via the QGIS
Processing R Provider algorithms (r:palimpsestrfit, r:palimpsestrintrusions),
which the dialog installs/updates into the Processing R scripts folder itself.

Modelled on tabs/Movecost.py. Drop this file into the pyArchInit `tabs/` folder
and wire it from pyarchinitPlugin.py (see the snippet at the bottom of this
file).

@author: Enzo Cocca <enzo.ccc@gmail.com>
"""
import os
from urllib.parse import urlparse

from qgis.PyQt.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QHBoxLayout, QLabel, QSpinBox,
    QDoubleSpinBox, QComboBox, QCheckBox, QLineEdit, QPushButton, QMessageBox,
    QPlainTextEdit)
from qgis.core import (QgsApplication, QgsCategorizedSymbolRenderer,
                       QgsRendererCategory, QgsSymbol, QgsProject)
from qgis.PyQt.QtGui import QColor
import processing

PHASE_COLOURS = ["#E69F00", "#56B4E9", "#009E73", "#CC79A7",
                 "#D55E00", "#0072B2", "#F0E442", "#999999"]

FIT_ALG = "r:palimpsestrfit"
INTRUSIONS_ALG = "r:palimpsestrintrusions"
REPORT_ALG = "r:palimpsestrreport"

# Processing R scripts shipped with palimpsestr, embedded so the dialog can
# install/update them itself.
RSX_SCRIPTS = {
    "palimpsestr_fit_db.rsx": r"""##palimpsestr=group
##Palimpsestr Fit=name
##Database_file=file
##Site=string all
##K=number 4
##Class_model=enum literal multinomial;gaussian
##Noise=boolean True
##Source=enum literal both;materials;pottery
##Phases=output vector
##Links=output vector
##Diagnostics=output table

# Probabilistic palimpsest decomposition straight from a pyArchInit SQLite/
# Spatialite database. Reads inventario_materiali + us (+ US polygon geometry)
# via read_pyarchinit(), fits the Stratigraphic Entanglement Field model, and
# returns a phase-assignment point layer, a high-SEI link layer, and a
# diagnostics table.
library(palimpsestr)
library(sf)
library(DBI)

con  <- DBI::dbConnect(RSQLite::SQLite(), Database_file)
geom <- tryCatch(sf::st_read(Database_file, layer = "pyunitastratigrafiche", quiet = TRUE),
                 error = function(e) NULL)

site       <- if (exists("Site") && nchar(Site) > 0 && Site != "all") Site else NULL
source_sel <- if (is.numeric(Source)) c("both", "materials", "pottery")[Source + 1] else as.character(Source)
d <- read_pyarchinit(con, us_geometry = geom, sito = site, source = source_sel)
DBI::dbDisconnect(con)

class_model <- if (is.numeric(Class_model)) c("multinomial", "gaussian")[Class_model + 1] else as.character(Class_model)
use_noise   <- isTRUE(as.logical(Noise))

fit <- fit_sef(d, k = as.integer(K), context = "context",
               tafonomy = "taf_score", class_model = class_model, noise = use_noise)
fit <- reorder_phases(fit)

crs_val <- if (!is.null(geom)) sf::st_crs(geom)$epsg else NA_integer_
if (is.null(crs_val) || is.na(crs_val)) crs_val <- NA_integer_

Phases      <- as_sf_phase(fit, crs = crs_val)
Links       <- as_sf_links(fit, crs = crs_val)
Diagnostics <- as_phase_table(fit)
""",
    "palimpsestr_intrusions_db.rsx": r"""##palimpsestr=group
##Palimpsestr Intrusions=name
##Database_file=file
##Site=string all
##K=number 4
##Threshold=number 0.5
##Source=enum literal both;materials;pottery
##Intrusions=output vector

# Model-based intrusion detection straight from a pyArchInit SQLite/Spatialite
# database. Fits the SEF model with a noise component and returns the finds as
# a point layer carrying the outlier posterior (intrusion_prob), the
# chronological direction, and the intrusion_type classification.
library(palimpsestr)
library(sf)
library(DBI)

con  <- DBI::dbConnect(RSQLite::SQLite(), Database_file)
geom <- tryCatch(sf::st_read(Database_file, layer = "pyunitastratigrafiche", quiet = TRUE),
                 error = function(e) NULL)

site       <- if (exists("Site") && nchar(Site) > 0 && Site != "all") Site else NULL
source_sel <- if (is.numeric(Source)) c("both", "materials", "pottery")[Source + 1] else as.character(Source)
d <- read_pyarchinit(con, us_geometry = geom, sito = site, source = source_sel)
DBI::dbDisconnect(con)

fit <- fit_sef(d, k = as.integer(K), context = "context",
               tafonomy = "taf_score", noise = TRUE)
fit <- reorder_phases(fit)
di <- detect_intrusions(fit, intrusion_threshold = Threshold)

crs_val <- if (!is.null(geom)) sf::st_crs(geom)$epsg else NA_integer_
if (is.null(crs_val) || is.na(crs_val)) crs_val <- NA_integer_

pts <- as_sf_phase(fit, crs = crs_val)
pts$intrusion_prob <- di$intrusion_prob
pts$direction      <- as.character(di$direction)
pts$intrusion_type <- as.character(di$intrusion_type)
Intrusions <- pts
""",
    "palimpsestr_report_db.rsx": r"""##palimpsestr=group
##Palimpsestr Report=name
##Database_file=file
##Site=string all
##K=number 4
##Class_model=enum literal multinomial;gaussian
##Noise=boolean True
##Source=enum literal both;materials;pottery
##Language=enum literal it;en
##Format=enum literal both;pdf;docx
##Report=output file

# Full narrated SEF report straight from a pyArchInit SQLite/Spatialite
# database. Reads finds (materials and/or pottery) via read_pyarchinit(), fits
# the Stratigraphic Entanglement Field model, and renders a PDF/DOCX report with
# the interpretive narrative, all gg_* diagnostic plots and diagnostic tables.
library(palimpsestr)
library(sf)
library(DBI)

con  <- DBI::dbConnect(RSQLite::SQLite(), Database_file)
geom <- tryCatch(sf::st_read(Database_file, layer = "pyunitastratigrafiche", quiet = TRUE),
                 error = function(e) NULL)

site        <- if (exists("Site") && nchar(Site) > 0 && Site != "all") Site else NULL
class_model <- if (is.numeric(Class_model)) c("multinomial", "gaussian")[Class_model + 1] else as.character(Class_model)
source_sel  <- if (is.numeric(Source))   c("both", "materials", "pottery")[Source + 1] else as.character(Source)
language    <- if (is.numeric(Language)) c("it", "en")[Language + 1] else as.character(Language)
fmt_sel     <- if (is.numeric(Format))   c("both", "pdf", "docx")[Format + 1] else as.character(Format)
fmt         <- if (fmt_sel == "both") c("pdf", "docx") else fmt_sel
use_noise   <- isTRUE(as.logical(Noise))

d <- read_pyarchinit(con, us_geometry = geom, sito = site, source = source_sel)
DBI::dbDisconnect(con)

fit <- fit_sef(d, k = as.integer(K), context = "context",
               tafonomy = "taf_score", class_model = class_model, noise = use_noise)
fit <- reorder_phases(fit)

written <- export_sef_report(fit, Report, format = fmt, lang = language, site = site)

# Make sure the declared Report output exists (export derives sibling files).
primary <- c(written[grepl("\\.pdf$",  written)],
             written[grepl("\\.docx$", written)],
             written[grepl("\\.md$",   written)])[1]
if (!is.na(primary) &&
    !identical(normalizePath(primary, mustWork = FALSE),
               normalizePath(Report,  mustWork = FALSE))) {
  file.copy(primary, Report, overwrite = TRUE)
}

cat("Report written:\n"); cat(paste0("  ", written), sep = "\n"); cat("\n")
""",
}


class pyarchinit_Palimpsest(QDialog):
    HOME = os.environ.get('PYARCHINIT_HOME', os.path.expanduser("~"))

    def __init__(self, iface):
        super().__init__()
        self.iface = iface
        self.setWindowTitle("palimpsestr \u2014 Palimpsest analysis")
        self._build_ui()
        self.install_scripts(silent=True)

    # ------------------------------------------------------------------ UI ---
    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(
            "Probabilistic palimpsest decomposition (SEF) on the active "
            "pyArchInit database."))

        form = QFormLayout()
        self.spin_k = QSpinBox(); self.spin_k.setRange(2, 12); self.spin_k.setValue(4)
        form.addRow("Number of phases (K):", self.spin_k)

        self.combo_model = QComboBox()
        self.combo_model.addItems(["multinomial (recommended)", "gaussian (legacy)"])
        form.addRow("Class model:", self.combo_model)

        self.check_noise = QCheckBox("Noise / outlier component"); self.check_noise.setChecked(True)
        form.addRow("", self.check_noise)

        self.spin_thr = QDoubleSpinBox(); self.spin_thr.setRange(0.0, 1.0)
        self.spin_thr.setSingleStep(0.05); self.spin_thr.setValue(0.5)
        form.addRow("Intrusion threshold:", self.spin_thr)

        # Source selector (maps to enum both=0, materials=1, pottery=2) — shared
        # by Fit, Intrusions and Report.
        self.combo_source = QComboBox()
        self.combo_source.addItems(["Entrambi", "Materiali", "Ceramica"])
        form.addRow("Reperti (source):", self.combo_source)

        # Report-only controls.
        self.combo_lang = QComboBox()
        self.combo_lang.addItems(["Italiano", "English"])
        form.addRow("Lingua report:", self.combo_lang)

        self.combo_format = QComboBox()
        self.combo_format.addItems(["PDF + DOCX", "PDF", "DOCX"])
        form.addRow("Formato report:", self.combo_format)

        self.edit_site = QLineEdit(); self.edit_site.setPlaceholderText("(all sites)")
        form.addRow("Site filter (optional):", self.edit_site)
        layout.addLayout(form)

        self.lbl_db = QLabel(self._describe_db())
        self.lbl_db.setWordWrap(True)
        layout.addWidget(self.lbl_db)

        buttons = QHBoxLayout()
        self.btn_fit = QPushButton("Fit SEF model"); self.btn_fit.clicked.connect(self.run_fit)
        self.btn_intr = QPushButton("Detect intrusions"); self.btn_intr.clicked.connect(self.run_intrusions)
        self.btn_report = QPushButton("Genera report (PDF/DOCX)")
        self.btn_report.clicked.connect(self.run_report)
        self.btn_install = QPushButton("Install/update R scripts")
        self.btn_install.clicked.connect(lambda: self.install_scripts(silent=False))
        buttons.addWidget(self.btn_fit); buttons.addWidget(self.btn_intr)
        buttons.addWidget(self.btn_report); buttons.addWidget(self.btn_install)
        layout.addLayout(buttons)

        # Report results panel + open buttons.
        self.results_panel = QPlainTextEdit()
        self.results_panel.setReadOnly(True)
        self.results_panel.setPlaceholderText(
            "The report narrative (markdown) will appear here after "
            "“Genera report”.")
        layout.addWidget(self.results_panel)

        self._report_pdf = None
        self._report_docx = None
        self._report_dir = None

        open_row = QHBoxLayout()
        self.btn_open_pdf = QPushButton("Apri PDF")
        self.btn_open_pdf.clicked.connect(lambda: self._open(self._report_pdf))
        self.btn_open_pdf.setEnabled(False)
        self.btn_open_docx = QPushButton("Apri DOCX")
        self.btn_open_docx.clicked.connect(lambda: self._open(self._report_docx))
        self.btn_open_docx.setEnabled(False)
        self.btn_open_dir = QPushButton("Apri cartella")
        self.btn_open_dir.clicked.connect(lambda: self._open(self._report_dir))
        self.btn_open_dir.setEnabled(False)
        open_row.addWidget(self.btn_open_pdf); open_row.addWidget(self.btn_open_docx)
        open_row.addWidget(self.btn_open_dir)
        layout.addLayout(open_row)

    # ----------------------------------------------------- active DB info ---
    def _active_conn_str(self):
        try:
            from ..modules.db.pyarchinit_conn_strings import Connection
        except Exception:
            try:
                from modules.db.pyarchinit_conn_strings import Connection
            except Exception:
                return None
        try:
            return Connection().conn_str()
        except Exception:
            return None

    def _sqlite_path(self):
        """Return the SQLite/Spatialite DB path, or None if not a SQLite DB."""
        cs = self._active_conn_str()
        if cs and cs.startswith('sqlite'):
            return cs.split('sqlite:///', 1)[-1]
        return None

    def _is_postgres(self):
        cs = self._active_conn_str()
        return bool(cs) and cs.startswith('postgres')

    def _describe_db(self):
        p = self._sqlite_path()
        if p:
            return "Active database (SQLite/Spatialite): %s" % p
        if self._is_postgres():
            return ("Active database is PostgreSQL. These algorithms currently "
                    "read SQLite/Spatialite databases; connect to a SQLite "
                    "pyArchInit database, or run read_pyarchinit() in R.")
        return "No active pyArchInit database connection detected."

    # ----------------------------------------------------------- run algos ---
    def _check_provider(self):
        if QgsApplication.processingRegistry().algorithmById(FIT_ALG) is None:
            QMessageBox.warning(
                self, "palimpsestr",
                "The palimpsestr Processing R scripts are not registered.\n\n"
                "Enable the 'Processing R Provider' plugin and restart QGIS. "
                "The scripts are installed automatically into the Processing R "
                "scripts folder when this dialog opens.")
            return False
        return True

    def _require_sqlite(self):
        path = self._sqlite_path()
        if not path:
            QMessageBox.warning(
                self, "palimpsestr",
                "No active SQLite/Spatialite pyArchInit connection.\n\n"
                "Connect to a SQLite pyArchInit database first.")
            return None
        if not os.path.exists(path):
            QMessageBox.warning(self, "palimpsestr",
                                "Database file not found:\n%s" % path)
            return None
        return path

    def _site(self):
        return self.edit_site.text().strip() or "all"

    def run_fit(self):
        if not self._check_provider():
            return
        path = self._require_sqlite()
        if not path:
            return
        import tempfile
        out = tempfile.mkdtemp(prefix="palimpsestr_")
        ph = os.path.join(out, "sef_phases.gpkg")
        lk = os.path.join(out, "sef_links.gpkg")
        dg = os.path.join(out, "sef_diagnostics.csv")
        params = {
            'Database_file': path,
            'Site': self._site(),
            'K': self.spin_k.value(),
            'Class_model': self.combo_model.currentIndex(),
            'Noise': self.check_noise.isChecked(),
            'Source': self.combo_source.currentIndex(),
            'Phases': ph, 'Links': lk, 'Diagnostics': dg}
        try:
            res = processing.run(FIT_ALG, params)
        except Exception as e:
            QMessageBox.critical(self, "palimpsestr", "Analysis failed:\n%s" % e)
            return
        n = self._load_outputs([(res.get('Phases', ph), "SEF phases", True),
                                (res.get('Links', lk), "SEF links", False)])
        if n == 0:
            QMessageBox.warning(self, "palimpsestr",
                "The analysis ran but produced no loadable layers (no finds with "
                "coordinates/dating?). Check the database content.")
        else:
            QMessageBox.information(self, "palimpsestr",
                "SEF analysis complete. Loaded %d layer(s)." % n)

    def run_intrusions(self):
        if not self._check_provider():
            return
        path = self._require_sqlite()
        if not path:
            return
        import tempfile
        out = tempfile.mkdtemp(prefix="palimpsestr_")
        ip = os.path.join(out, "sef_intrusions.gpkg")
        params = {
            'Database_file': path,
            'Site': self._site(),
            'K': self.spin_k.value(),
            'Threshold': self.spin_thr.value(),
            'Source': self.combo_source.currentIndex(),
            'Intrusions': ip}
        try:
            res = processing.run(INTRUSIONS_ALG, params)
        except Exception as e:
            QMessageBox.critical(self, "palimpsestr", "Analysis failed:\n%s" % e)
            return
        n = self._load_outputs([(res.get('Intrusions', ip), "SEF intrusions", False)])
        if n == 0:
            QMessageBox.warning(self, "palimpsestr",
                "The analysis ran but produced no loadable layer.")
        else:
            QMessageBox.information(self, "palimpsestr",
                "Intrusion detection complete. Loaded %d layer(s)." % n)

    # -------------------------------------------------------------- report ---
    def _check_provider_report(self):
        if QgsApplication.processingRegistry().algorithmById(REPORT_ALG) is None:
            QMessageBox.warning(
                self, "palimpsestr",
                "The palimpsestr report Processing R script is not registered.\n\n"
                "Enable the 'Processing R Provider' plugin and restart QGIS. "
                "The scripts are installed automatically into the Processing R "
                "scripts folder when this dialog opens.")
            return False
        return True

    def _augment_render_env(self):
        """Make pandoc + a LaTeX engine discoverable by the R subprocess.

        QGIS (a GUI app) launches with a minimal PATH that usually omits
        Homebrew (/opt/homebrew/bin), MacTeX (/Library/TeX/texbin) and
        TinyTeX, so rmarkdown's pandoc/LaTeX discovery fails and the report
        silently falls back to markdown only (no PDF/DOCX). Probe common
        install locations and prepend the ones we find to PATH (+ set
        RSTUDIO_PANDOC, which rmarkdown honours) for this process and the R
        child it spawns. Returns (pandoc_found, latex_found).
        """
        import glob
        home = os.path.expanduser("~")
        is_win = os.name == "nt"
        exe = ".exe" if is_win else ""
        pandoc_dirs = [
            "/opt/homebrew/bin", "/usr/local/bin", "/usr/bin",
            "/Applications/RStudio.app/Contents/Resources/app/bin/quarto/bin/tools",
            "/Applications/RStudio.app/Contents/Resources/app/bin/pandoc",
            "/Applications/RStudio.app/Contents/MacOS/pandoc",
            "/Applications/quarto/bin/tools"]
        latex_dirs = ["/Library/TeX/texbin", "/usr/local/bin",
                      "/opt/homebrew/bin", "/usr/bin"]
        latex_dirs += glob.glob(os.path.join(home, "Library", "TinyTeX", "bin", "*"))
        latex_dirs += glob.glob(os.path.join(home, ".TinyTeX", "bin", "*"))
        if is_win:
            la = os.environ.get("LOCALAPPDATA", "")
            ap = os.environ.get("APPDATA", "")
            pandoc_dirs += [os.path.join(la, "Pandoc"), r"C:\Program Files\Pandoc",
                            r"C:\Program Files\RStudio\resources\app\bin\quarto\bin\tools"]
            latex_dirs += [os.path.join(ap, "TinyTeX", "bin", "windows"),
                           os.path.join(la, "Programs", "MiKTeX", "miktex", "bin", "x64")]

        def _first_with(dirs, names):
            for d in dirs:
                if d and any(os.path.isfile(os.path.join(d, n)) for n in names):
                    return d
            return None

        extra = []
        pandoc_dir = _first_with(pandoc_dirs, ["pandoc" + exe])
        if pandoc_dir:
            if not os.environ.get("RSTUDIO_PANDOC"):
                os.environ["RSTUDIO_PANDOC"] = pandoc_dir
            extra.append(pandoc_dir)
        latex_dir = _first_with(
            latex_dirs, ["pdflatex" + exe, "xelatex" + exe, "tlmgr" + exe])
        if latex_dir:
            extra.append(latex_dir)
        if extra:
            sep = os.pathsep
            parts = os.environ.get("PATH", "").split(sep)
            os.environ["PATH"] = sep.join(
                [d for d in extra if d not in parts] + parts)
        return pandoc_dir is not None, latex_dir is not None

    def run_report(self):
        if not self._check_provider_report():
            return
        path = self._require_sqlite()
        if not path:
            return
        # QGIS's minimal GUI PATH usually hides pandoc/LaTeX from R; make them
        # discoverable so the report renders to PDF/DOCX rather than only .md.
        pandoc_ok, _latex_ok = self._augment_render_env()
        import tempfile
        out_dir = tempfile.mkdtemp(prefix="palimpsestr_report_")
        report = os.path.join(out_dir, "sef_report.pdf")
        params = {
            'Database_file': path,
            'Site': self._site(),
            'K': self.spin_k.value(),
            'Class_model': self.combo_model.currentIndex(),
            'Noise': self.check_noise.isChecked(),
            'Source': self.combo_source.currentIndex(),
            'Language': self.combo_lang.currentIndex(),
            'Format': self.combo_format.currentIndex(),
            'Report': report}
        try:
            processing.run(REPORT_ALG, params)
        except Exception as e:
            QMessageBox.critical(self, "palimpsestr", "Report failed:\n%s" % e)
            return
        base = os.path.splitext(report)[0]
        self._show_report(base, pandoc_ok)

    @staticmethod
    def _has_magic(path, magic):
        try:
            with open(path, "rb") as f:
                return f.read(len(magic)) == magic
        except Exception:
            return False

    def _show_report(self, base, pandoc_ok=True):
        """Load the markdown narrative into the panel and enable open buttons."""
        md = base + ".md"
        if os.path.exists(md):
            with open(md, encoding="utf-8") as f:
                self.results_panel.setPlainText(f.read())
        else:
            self.results_panel.setPlainText(
                "The report ran but no markdown narrative was found next to:\n"
                "%s" % base)
        # Validate by content, not extension: when pandoc/LaTeX are missing the
        # algorithm copies the .md onto the declared .pdf output, so a file with
        # a .pdf name may actually be markdown. Only offer genuine files
        # (PDF starts with %PDF, DOCX is a zip starting with PK\x03\x04).
        pdf, docx = base + ".pdf", base + ".docx"
        self._report_pdf = pdf if self._has_magic(pdf, b"%PDF") else None
        self._report_docx = docx if self._has_magic(docx, b"PK\x03\x04") else None
        self._report_dir = os.path.dirname(base)
        self.btn_open_pdf.setEnabled(bool(self._report_pdf))
        self.btn_open_docx.setEnabled(bool(self._report_docx))
        self.btn_open_dir.setEnabled(True)
        # No genuine PDF/DOCX → only the markdown narrative was rendered.
        if not self._report_pdf and not self._report_docx:
            if pandoc_ok:
                hint = ("Only the Markdown narrative could be produced.\n\n"
                        "pandoc was found but a LaTeX engine is needed for PDF "
                        "(install with tinytex::install_tinytex() in R). The "
                        "narrative above and the PNG figures in the report "
                        "folder are complete.")
            else:
                hint = ("Only the Markdown narrative could be produced because "
                        "pandoc/LaTeX were not found.\n\n"
                        "Install pandoc and a LaTeX engine (in R: "
                        "tinytex::install_tinytex()), then run the report "
                        "again. The narrative above and the PNG figures in the "
                        "report folder are complete.")
            QMessageBox.information(self, "palimpsestr", hint)

    def _open(self, p):
        from qgis.PyQt.QtGui import QDesktopServices
        from qgis.PyQt.QtCore import QUrl
        if p:
            QDesktopServices.openUrl(QUrl.fromLocalFile(p))

    def _load_outputs(self, items):
        """Load (path, name, is_phase) outputs into the project; return count."""
        from qgis.core import QgsVectorLayer
        loaded = 0
        first = None
        for spec in items:
            pth, name, is_phase = spec
            if not pth or not os.path.exists(pth):
                continue
            lyr = QgsVectorLayer(pth, name, "ogr")
            if not lyr.isValid() or lyr.featureCount() == 0:
                continue
            QgsProject.instance().addMapLayer(lyr)
            loaded += 1
            if first is None:
                first = lyr
            if is_phase:
                self._style_phases(lyr)
        if first is not None:
            try:
                self.iface.setActiveLayer(first)
                self.iface.zoomToActiveLayer()
            except Exception:
                pass
        return loaded

    # --------------------------------------------------- install R scripts ---
    def _scripts_folder(self):
        try:
            from processing.tools.system import userFolder
            base = userFolder()
        except Exception:
            base = os.path.join(QgsApplication.qgisSettingsDirPath(), 'processing')
        folder = os.path.join(base, 'rscripts')
        os.makedirs(folder, exist_ok=True)
        return folder

    def install_scripts(self, silent=False):
        """Copy/overwrite the bundled .rsx into the Processing R scripts folder."""
        folder = self._scripts_folder()
        try:
            for name, content in RSX_SCRIPTS.items():
                with open(os.path.join(folder, name), 'w', encoding='utf-8') as f:
                    f.write(content)
            try:
                QgsApplication.processingRegistry().providerById('r').refreshAlgorithms()
            except Exception:
                pass
        except Exception as e:
            if not silent:
                QMessageBox.critical(self, "palimpsestr", "Could not install R scripts:\n%s" % e)
            return False
        if not silent:
            QMessageBox.information(self, "palimpsestr",
                "Installed/updated %d R scripts in:\n%s" % (len(RSX_SCRIPTS), folder))
        return True

    # ----------------------------------------------------------- styling ----
    def _style_phases(self, layer_id):
        layer = None
        if layer_id:
            layer = QgsProject.instance().mapLayer(layer_id) if isinstance(layer_id, str) else layer_id
        if layer is None:
            return
        try:
            field = "dominant_phase"
            phases = sorted({f[field] for f in layer.getFeatures() if f[field] is not None})
            categories = []
            for i, ph in enumerate(phases):
                sym = QgsSymbol.defaultSymbol(layer.geometryType())
                sym.setColor(QColor(PHASE_COLOURS[i % len(PHASE_COLOURS)]))
                categories.append(QgsRendererCategory(ph, sym, "phase %s" % ph))
            layer.setRenderer(QgsCategorizedSymbolRenderer(field, categories))
            layer.triggerRepaint()
        except Exception:
            pass


# ---------------------------------------------------------------------------
# Wiring in pyarchinitPlugin.py (mirroring actionMovecost), e.g. in initGui():
#
#   self.actionPalimpsest = QAction("palimpsestr - Analisi palinsesti",
#                                    self.iface.mainWindow())
#   self.actionPalimpsest.triggered.connect(self.runPalimpsest)
#   self.analysisToolButton.addActions([self.actionPalimpsest])
#
#   def runPalimpsest(self):
#       from .tabs.Palimpsest import pyarchinit_Palimpsest
#       dlg = pyarchinit_Palimpsest(self.iface)
#       dlg.show()
#       self.pluginGui = dlg
# ---------------------------------------------------------------------------
