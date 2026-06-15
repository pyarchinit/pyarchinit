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
from urllib.parse import urlparse, parse_qs

from qgis.PyQt.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QHBoxLayout, QLabel, QSpinBox,
    QDoubleSpinBox, QComboBox, QCheckBox, QLineEdit, QPushButton, QMessageBox,
    QPlainTextEdit, QTableWidget, QTableWidgetItem, QHeaderView, QFileDialog)
from qgis.core import (QgsApplication, QgsCategorizedSymbolRenderer,
                       QgsRendererCategory, QgsSymbol, QgsProject)
from qgis.PyQt.QtGui import QColor
import processing

PHASE_COLOURS = ["#E69F00", "#56B4E9", "#009E73", "#CC79A7",
                 "#D55E00", "#0072B2", "#F0E442", "#999999"]

FIT_ALG = "r:palimpsestrfit"
INTRUSIONS_ALG = "r:palimpsestrintrusions"
REPORT_ALG = "r:palimpsestrreport"

# Optional per-US absolute-chronology table that read_pyarchinit() auto-detects
# and uses in place of the free-text datazione (palimpsestr >= 0.22.0).
CHRONOLOGY_TABLE = "palimpsest_chronology"

# Plain Rscript driver (NOT a Processing .rsx) that calibrates radiocarbon dates
# with OxCal via oxcAAR and reduces them to a calendar interval with
# palimpsestr::chronology_from_oxcal(). Reads a samples CSV (id,c14_bp,c14_error)
# and writes an out CSV (id,start,end) with calendar years (BCE negative). The
# table write itself is done in Python so it honours the active backend.
CHRONO_OXCAL_R = r"""args <- commandArgs(trailingOnly = TRUE)
samples_csv <- args[1]; out_csv <- args[2]
suppressMessages({ library(oxcAAR); library(palimpsestr) })
s <- read.csv(samples_csv, stringsAsFactors = FALSE, colClasses = "character")
# Persistent OxCal engine: install once into a stable directory (override with
# the PYARCHINIT_OXCAL_DIR env var) and reuse it across R sessions via
# setOxcalExecutablePath(), instead of re-downloading into tempdir() each run.
oxcal_dir <- Sys.getenv("PYARCHINIT_OXCAL_DIR",
                        unset = file.path(path.expand("~"), ".pyarchinit", "oxcal"))
oxcal_exe <- switch(Sys.info()[["sysname"]],
  Darwin  = file.path(oxcal_dir, "OxCal", "bin", "OxCalMac"),
  Windows = file.path(oxcal_dir, "OxCal", "bin", "OxCalWin.exe"),
  file.path(oxcal_dir, "OxCal", "bin", "OxCalLinux"))
if (file.exists(oxcal_exe)) {
  oxcAAR::setOxcalExecutablePath(oxcal_exe)
} else {
  dir.create(oxcal_dir, recursive = TRUE, showWarnings = FALSE)
  oxcAAR::quickSetupOxcal(path = oxcal_dir)
}
ids <- as.character(s$id)
cal <- oxcAAR::oxcalCalibrate(as.numeric(s$c14_bp), as.numeric(s$c14_error), ids)
res <- palimpsestr::chronology_from_oxcal(cal, ids = ids, bce_negative = TRUE)
out <- data.frame(id = as.character(res$id),
                  start = as.integer(round(res$date_min)),
                  end   = as.integer(round(res$date_max)),
                  stringsAsFactors = FALSE)
write.csv(out, out_csv, row.names = FALSE)
cat("calibrated ", nrow(out), " sample(s)\n", sep = "")
"""

# Processing R scripts shipped with palimpsestr, embedded so the dialog can
# install/update them itself.
RSX_SCRIPTS = {
    "palimpsestr_fit_db.rsx": r"""##palimpsestr=group
##Palimpsestr Fit=name
##Database_file=optional file
##PG_connection=optional string
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

# Connection: PostgreSQL/PostGIS when PG_connection (a libpq DSN, e.g.
# "host=... port=5432 dbname=pyarchinit user=... password=...") is given,
# otherwise the SQLite/Spatialite Database_file.
use_pg <- exists("PG_connection") && is.character(PG_connection) && nzchar(PG_connection)
if (use_pg) {
  con  <- DBI::dbConnect(RPostgres::Postgres(), dbname = PG_connection)
  geom <- tryCatch(sf::st_read(con, query = "SELECT us_s, the_geom FROM pyunitastratigrafiche", quiet = TRUE),
                   error = function(e) NULL)
} else {
  con  <- DBI::dbConnect(RSQLite::SQLite(), Database_file)
  geom <- tryCatch(sf::st_read(Database_file, layer = "pyunitastratigrafiche", quiet = TRUE),
                   error = function(e) NULL)
}

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
##Database_file=optional file
##PG_connection=optional string
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

# Connection: PostgreSQL/PostGIS when PG_connection (a libpq DSN) is given,
# otherwise the SQLite/Spatialite Database_file.
use_pg <- exists("PG_connection") && is.character(PG_connection) && nzchar(PG_connection)
if (use_pg) {
  con  <- DBI::dbConnect(RPostgres::Postgres(), dbname = PG_connection)
  geom <- tryCatch(sf::st_read(con, query = "SELECT us_s, the_geom FROM pyunitastratigrafiche", quiet = TRUE),
                   error = function(e) NULL)
} else {
  con  <- DBI::dbConnect(RSQLite::SQLite(), Database_file)
  geom <- tryCatch(sf::st_read(Database_file, layer = "pyunitastratigrafiche", quiet = TRUE),
                   error = function(e) NULL)
}

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
##Database_file=optional file
##PG_connection=optional string
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

# Connection: PostgreSQL/PostGIS when PG_connection (a libpq DSN) is given,
# otherwise the SQLite/Spatialite Database_file.
use_pg <- exists("PG_connection") && is.character(PG_connection) && nzchar(PG_connection)
if (use_pg) {
  con  <- DBI::dbConnect(RPostgres::Postgres(), dbname = PG_connection)
  geom <- tryCatch(sf::st_read(con, query = "SELECT us_s, the_geom FROM pyunitastratigrafiche", quiet = TRUE),
                   error = function(e) NULL)
} else {
  con  <- DBI::dbConnect(RSQLite::SQLite(), Database_file)
  geom <- tryCatch(sf::st_read(Database_file, layer = "pyunitastratigrafiche", quiet = TRUE),
                   error = function(e) NULL)
}

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

        # Absolute chronology (OxCal) — optional per-US dating table.
        chrono_row = QHBoxLayout()
        self.btn_chrono = QPushButton("Cronologia assoluta (OxCal)…")
        self.btn_chrono.setToolTip(
            "Crea/popola la tabella palimpsest_chronology (date calibrate "
            "per US) usata da palimpsestr al posto della datazione testuale.")
        self.btn_chrono.clicked.connect(self.open_chronology)
        self.btn_ai = QPushButton("Report AI (analisi descrittiva)…")
        self.btn_ai.setToolTip(
            "Genera una relazione descrittiva dell'analisi SEF con agenti AI "
            "specializzati (metodologo, analista, redattore), in qualsiasi "
            "lingua, con spiegazione delle scelte di modello/K/soglia e figure.")
        self.btn_ai.clicked.connect(self.open_ai_report)
        chrono_row.addWidget(self.btn_chrono)
        chrono_row.addWidget(self.btn_ai)
        layout.addLayout(chrono_row)

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

    def _pg_dsn(self):
        """libpq DSN from the active SQLAlchemy URL, or None if not PostgreSQL.

        pyArchInit stores e.g.
        ``postgresql://user:pwd@host:5432/db?sslmode=allow``; palimpsestr's
        .rsx connect with ``RPostgres::Postgres(dbname = <DSN>)``.
        """
        cs = self._active_conn_str()
        if not cs or not cs.startswith('postgres'):
            return None
        u = urlparse(cs)
        parts = []
        if u.hostname:
            parts.append("host=%s" % u.hostname)
        if u.port:
            parts.append("port=%s" % u.port)
        if u.path and u.path != '/':
            parts.append("dbname=%s" % u.path.lstrip('/'))
        if u.username:
            parts.append("user=%s" % u.username)
        if u.password:
            parts.append("password=%s" % u.password)
        qs = parse_qs(u.query)
        if qs.get('sslmode'):
            parts.append("sslmode=%s" % qs['sslmode'][0])
        return " ".join(parts)

    def _db_params(self):
        """Processing params selecting the active backend, or None.

        PostgreSQL/PostGIS when a PG connection is active (``PG_connection``
        libpq DSN), otherwise the SQLite/Spatialite ``Database_file``. Warns
        and returns None when nothing usable is connected.
        """
        dsn = self._pg_dsn()
        if dsn:
            return {'PG_connection': dsn}
        path = self._require_sqlite()
        if not path:
            return None
        return {'Database_file': path}

    def _describe_db(self):
        p = self._sqlite_path()
        if p:
            return "Active database (SQLite/Spatialite): %s" % p
        if self._is_postgres():
            u = urlparse(self._active_conn_str())
            where = "%s/%s" % (u.hostname or "?", (u.path or "").lstrip('/') or "?")
            return ("Active database (PostgreSQL/PostGIS): %s. The palimpsestr "
                    "algorithms read it directly." % where)
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
        db = self._db_params()
        if db is None:
            return
        import tempfile
        out = tempfile.mkdtemp(prefix="palimpsestr_")
        ph = os.path.join(out, "sef_phases.gpkg")
        lk = os.path.join(out, "sef_links.gpkg")
        dg = os.path.join(out, "sef_diagnostics.csv")
        params = {
            'Site': self._site(),
            'K': self.spin_k.value(),
            'Class_model': self.combo_model.currentIndex(),
            'Noise': self.check_noise.isChecked(),
            'Source': self.combo_source.currentIndex(),
            'Phases': ph, 'Links': lk, 'Diagnostics': dg}
        params.update(db)
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
        db = self._db_params()
        if db is None:
            return
        import tempfile
        out = tempfile.mkdtemp(prefix="palimpsestr_")
        ip = os.path.join(out, "sef_intrusions.gpkg")
        params = {
            'Site': self._site(),
            'K': self.spin_k.value(),
            'Threshold': self.spin_thr.value(),
            'Source': self.combo_source.currentIndex(),
            'Intrusions': ip}
        params.update(db)
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
        db = self._db_params()
        if db is None:
            return
        # QGIS's minimal GUI PATH usually hides pandoc/LaTeX from R; make them
        # discoverable so the report renders to PDF/DOCX rather than only .md.
        pandoc_ok, _latex_ok = self._augment_render_env()
        import tempfile
        out_dir = tempfile.mkdtemp(prefix="palimpsestr_report_")
        report = os.path.join(out_dir, "sef_report.pdf")
        params = {
            'Site': self._site(),
            'K': self.spin_k.value(),
            'Class_model': self.combo_model.currentIndex(),
            'Noise': self.check_noise.isChecked(),
            'Source': self.combo_source.currentIndex(),
            'Language': self.combo_lang.currentIndex(),
            'Format': self.combo_format.currentIndex(),
            'Report': report}
        params.update(db)
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

    def open_chronology(self):
        if not (self._pg_dsn() or self._sqlite_path()):
            QMessageBox.warning(
                self, "palimpsestr",
                "No active pyArchInit database connection.\n\n"
                "Connect to a SQLite or PostgreSQL pyArchInit database first.")
            return
        dlg = PalimpsestChronologyDialog(self)
        dlg.exec()

    # ------------------------------------------------------------ AI report ---
    def _has_chronology(self):
        """True if palimpsest_chronology exists with rows for the active site."""
        site = self.edit_site.text().strip()
        try:
            dsn = self._pg_dsn()
            if dsn:
                import psycopg2
                conn = psycopg2.connect(dsn); ph = "%s"
            else:
                path = self._sqlite_path()
                if not path or not os.path.exists(path):
                    return False
                import sqlite3
                conn = sqlite3.connect(path); ph = "?"
            try:
                cur = conn.cursor()
                if site and site != "all":
                    cur.execute("SELECT COUNT(*) FROM %s WHERE sito = %s"
                                % (CHRONOLOGY_TABLE, ph), (site,))
                else:
                    cur.execute("SELECT COUNT(*) FROM %s" % CHRONOLOGY_TABLE)
                return (cur.fetchone() or [0])[0] > 0
            finally:
                conn.close()
        except Exception:
            return False

    def _gather_sef_facts(self):
        """Run the SEF report (R) and collect facts for the AI agents, or None."""
        db = self._db_params()
        if db is None:
            return None
        self._augment_render_env()
        import tempfile
        out_dir = tempfile.mkdtemp(prefix="palimpsestr_ai_")
        report = os.path.join(out_dir, "sef_report.pdf")
        params = {
            'Site': self._site(),
            'K': self.spin_k.value(),
            'Class_model': self.combo_model.currentIndex(),
            'Noise': self.check_noise.isChecked(),
            'Source': self.combo_source.currentIndex(),
            'Language': self.combo_lang.currentIndex(),
            'Format': self.combo_format.currentIndex(),
            'Report': report}
        params.update(db)
        from qgis.PyQt.QtWidgets import QApplication
        from qgis.PyQt.QtCore import Qt
        QApplication.setOverrideCursor(Qt.WaitCursor)
        try:
            processing.run(REPORT_ALG, params)
        except Exception as e:
            QApplication.restoreOverrideCursor()
            QMessageBox.critical(self, "palimpsestr",
                                 "Analisi SEF (R) fallita:\n%s" % e)
            return None
        finally:
            QApplication.restoreOverrideCursor()
        base = os.path.splitext(report)[0]
        md = base + ".md"
        r_markdown = ""
        if os.path.exists(md):
            with open(md, encoding="utf-8") as f:
                r_markdown = f.read()
        figs_dir = base + "_figs"
        figures = []
        if os.path.isdir(figs_dir):
            figures = sorted(os.path.splitext(f)[0]
                             for f in os.listdir(figs_dir) if f.endswith(".png"))
        from .palimpsest_ai_report import _model_name, _source_name
        return {
            "site": self._site(),
            "backend": "PostgreSQL/PostGIS" if self._pg_dsn() else "SQLite/Spatialite",
            "k": self.spin_k.value(),
            "class_model": _model_name(self.combo_model.currentIndex()),
            "noise": self.check_noise.isChecked(),
            "threshold": self.spin_thr.value(),
            "source": _source_name(self.combo_source.currentIndex()),
            "has_chronology": self._has_chronology(),
            "r_markdown": r_markdown,
            "figures": figures,
            "figures_dir": figs_dir,
        }

    def open_ai_report(self):
        if not self._check_provider_report():
            return
        if not (self._pg_dsn() or self._sqlite_path()):
            QMessageBox.warning(
                self, "palimpsestr",
                "Nessuna connessione al database attiva.\n\n"
                "Connetti un database pyArchInit (SQLite o PostgreSQL).")
            return
        facts = self._gather_sef_facts()
        if facts is None:
            return
        if not facts.get("r_markdown"):
            QMessageBox.warning(
                self, "palimpsestr",
                "L'analisi SEF non ha prodotto una narrativa leggibile "
                "(dati insufficienti?). Verifica il contenuto del database.")
            return
        from .palimpsest_ai_report import PalimpsestAIReportDialog
        dlg = PalimpsestAIReportDialog(self, facts)
        dlg.exec()

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


def _stretch_mode():
    """QHeaderView Stretch resize mode, across PyQt5 (Qt5) and PyQt6 (Qt6)."""
    try:
        return QHeaderView.ResizeMode.Stretch
    except AttributeError:
        return QHeaderView.Stretch


class PalimpsestChronologyDialog(QDialog):
    """Create/populate the optional ``palimpsest_chronology`` table.

    palimpsestr >= 0.22.0's ``read_pyarchinit()`` auto-detects this per-US
    table and uses its calibrated ``start``/``end`` (calendar years, BCE
    negative) in place of the free-text ``datazione``. Two ways to fill it:
    enter radiocarbon dates and calibrate them with OxCal (oxcAAR +
    ``chronology_from_oxcal``), or import a CSV of already-calibrated ranges.
    The table write honours the active backend (SQLite or PostgreSQL).
    """

    def __init__(self, parent_dlg):
        super().__init__(parent_dlg)
        self.p = parent_dlg
        self.setWindowTitle("palimpsestr — Cronologia assoluta (OxCal)")
        self.resize(700, 440)
        self._build_ui()

    def _build_ui(self):
        lay = QVBoxLayout(self)
        lay.addWidget(QLabel(
            "Date assolute per US nella tabella <b>palimpsest_chronology</b>, "
            "usata da palimpsestr al posto della datazione testuale.<br>"
            "Inserisci le date radiocarboniche (BP ± errore) e premi "
            "<b>Calibra e salva</b> per ottenere gli intervalli calendariali "
            "via OxCal, oppure importa un CSV già calibrato "
            "(<i>sito, area, us, start, end, lab_code, source</i>)."))

        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(
            ["Sito", "Area", "US", "C14 BP", "± errore", "Lab code"])
        self.table.horizontalHeader().setSectionResizeMode(_stretch_mode())
        lay.addWidget(self.table)
        site = self.p.edit_site.text().strip()
        self._add_row(site if site and site != "all" else "")

        row1 = QHBoxLayout()
        b_add = QPushButton("Aggiungi riga")
        b_add.clicked.connect(lambda: self._add_row())
        b_del = QPushButton("Rimuovi riga")
        b_del.clicked.connect(self._remove_row)
        b_imps = QPushButton("Importa campioni CSV…")
        b_imps.clicked.connect(self._import_samples_csv)
        row1.addWidget(b_add); row1.addWidget(b_del); row1.addWidget(b_imps)
        lay.addLayout(row1)

        row2 = QHBoxLayout()
        b_ddl = QPushButton("Crea/aggiorna tabella")
        b_ddl.clicked.connect(self._create_table)
        b_cal = QPushButton("Calibra e salva (OxCal)")
        b_cal.clicked.connect(self._calibrate_and_save)
        b_impc = QPushButton("Importa range calibrati (CSV)…")
        b_impc.clicked.connect(self._import_calibrated_csv)
        b_close = QPushButton("Chiudi")
        b_close.clicked.connect(self.accept)
        row2.addWidget(b_ddl); row2.addWidget(b_cal)
        row2.addWidget(b_impc); row2.addWidget(b_close)
        lay.addLayout(row2)

        self.status = QLabel("")
        self.status.setWordWrap(True)
        lay.addWidget(self.status)

    # --------------------------------------------------------------- table ---
    def _add_row(self, sito="", area="", us="", bp="", err="", lab=""):
        r = self.table.rowCount()
        self.table.insertRow(r)
        for c, v in enumerate([sito, area, us, bp, err, lab]):
            self.table.setItem(r, c, QTableWidgetItem("" if v is None else str(v)))

    def _remove_row(self):
        rows = sorted({i.row() for i in self.table.selectedIndexes()}, reverse=True)
        for r in rows:
            self.table.removeRow(r)

    def _collect_rows(self, require_c14):
        """Read the table into dicts; show a message and return None on error."""
        rows = []
        for r in range(self.table.rowCount()):
            def cell(c):
                it = self.table.item(r, c)
                return it.text().strip() if it and it.text() else ""
            sito, area, us = cell(0), cell(1) or None, cell(2)
            bp, err, lab = cell(3), cell(4), cell(5) or None
            if not any([sito, area, us, bp, err, lab]):
                continue
            if not sito or not us:
                QMessageBox.warning(self, "palimpsestr",
                                    "Riga %d: Sito e US sono obbligatori." % (r + 1))
                return None
            try:
                us_i = int(us)
            except ValueError:
                QMessageBox.warning(self, "palimpsestr",
                                    "Riga %d: US dev'essere un intero." % (r + 1))
                return None
            rec = {"sito": sito, "area": area, "us": us_i, "lab_code": lab}
            if require_c14:
                try:
                    rec["c14_bp"] = float(bp)
                    rec["c14_error"] = float(err)
                except ValueError:
                    QMessageBox.warning(
                        self, "palimpsestr",
                        "Riga %d: C14 BP ed errore devono essere numeri." % (r + 1))
                    return None
            rows.append(rec)
        return rows

    # ----------------------------------------------------------- backend DB ---
    def _conn(self):
        """(connection, kind, placeholder) for the active backend, or None."""
        dsn = self.p._pg_dsn()
        if dsn:
            try:
                import psycopg2
            except Exception as e:
                QMessageBox.critical(self, "palimpsestr",
                                     "psycopg2 is required for PostgreSQL:\n%s" % e)
                return None, None, None
            return psycopg2.connect(dsn), "pg", "%s"
        path = self.p._sqlite_path()
        if path and os.path.exists(path):
            import sqlite3
            return sqlite3.connect(path), "sqlite", "?"
        QMessageBox.warning(self, "palimpsestr",
                            "Nessuna connessione al database attiva.")
        return None, None, None

    def _ddl(self, conn, kind):
        pk = "SERIAL PRIMARY KEY" if kind == "pg" else "INTEGER PRIMARY KEY"
        # "start"/"end" quoted: end is a reserved word in PostgreSQL.
        conn.cursor().execute(
            'CREATE TABLE IF NOT EXISTS %s ('
            ' id %s, sito TEXT, area TEXT, us INTEGER,'
            ' "start" INTEGER, "end" INTEGER, lab_code TEXT, source TEXT)'
            % (CHRONOLOGY_TABLE, pk))
        conn.commit()

    def _save_rows(self, rows):
        """Upsert (sito,area,us)-keyed rows; returns the count written."""
        conn, kind, ph = self._conn()
        if conn is None:
            return 0
        try:
            self._ddl(conn, kind)
            cur = conn.cursor()
            for (sito, area, us, start, end, lab, source) in rows:
                cur.execute(
                    "DELETE FROM %s WHERE sito = %s AND us = %s "
                    "AND COALESCE(area,'') = COALESCE(%s,'')"
                    % (CHRONOLOGY_TABLE, ph, ph, ph), (sito, us, area))
                cur.execute(
                    'INSERT INTO %s (sito, area, us, "start", "end", lab_code, '
                    'source) VALUES (%s, %s, %s, %s, %s, %s, %s)'
                    % (CHRONOLOGY_TABLE, ph, ph, ph, ph, ph, ph, ph),
                    (sito, area, us, start, end, lab, source))
            conn.commit()
            return len(rows)
        except Exception as e:
            try:
                conn.rollback()
            except Exception:
                pass
            QMessageBox.critical(self, "palimpsestr", "Scrittura fallita:\n%s" % e)
            return 0
        finally:
            conn.close()

    def _create_table(self):
        conn, kind, _ph = self._conn()
        if conn is None:
            return
        try:
            self._ddl(conn, kind)
        except Exception as e:
            QMessageBox.critical(self, "palimpsestr",
                                 "Creazione tabella fallita:\n%s" % e)
            return
        finally:
            conn.close()
        self.status.setText("Tabella %s pronta (%s)." % (CHRONOLOGY_TABLE, kind))
        QMessageBox.information(self, "palimpsestr",
                               "Tabella %s pronta." % CHRONOLOGY_TABLE)

    # ------------------------------------------------------- OxCal calibrate ---
    def _find_rscript(self):
        import glob
        exe = "Rscript.exe" if os.name == "nt" else "Rscript"
        cands = []
        try:
            from qgis.core import QgsSettings
            folder = QgsSettings().value("Processing/Configuration/R_FOLDER", "",
                                         type=str)
            if folder:
                cands += [os.path.join(folder, exe),
                          os.path.join(folder, "bin", exe)]
        except Exception:
            pass
        cands += ["/usr/local/bin/" + exe, "/opt/homebrew/bin/" + exe,
                  "/usr/bin/" + exe]
        if os.name == "nt":
            cands += glob.glob(r"C:\Program Files\R\R-*\bin\\" + exe)
        for c in cands:
            if c and os.path.isfile(c):
                return c
        return exe  # rely on PATH as a last resort

    def _calibrate(self, samples):
        """Run the OxCal driver; returns {id: (start, end)} or None on failure."""
        import tempfile, subprocess, csv
        d = tempfile.mkdtemp(prefix="palimpsestr_chrono_")
        sin = os.path.join(d, "samples.csv")
        sout = os.path.join(d, "calibrated.csv")
        rdrv = os.path.join(d, "calibrate.R")
        with open(sin, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["id", "c14_bp", "c14_error"])
            for s in samples:
                w.writerow([s["id"], s["c14_bp"], s["c14_error"]])
        with open(rdrv, "w", encoding="utf-8") as f:
            f.write(CHRONO_OXCAL_R)
        # Help the R child find tools (pandoc not needed here, but java/oxcal
        # may live in dirs hidden from QGIS's minimal GUI PATH).
        try:
            self.p._augment_render_env()
        except Exception:
            pass
        rscript = self._find_rscript()
        try:
            proc = subprocess.run([rscript, rdrv, sin, sout],
                                  capture_output=True, text=True, timeout=3600)
        except Exception as e:
            QMessageBox.critical(self, "palimpsestr",
                                 "Impossibile eseguire R (Rscript):\n%s" % e)
            return None
        if proc.returncode != 0 or not os.path.exists(sout):
            msg = (proc.stderr or proc.stdout or "")[-2000:]
            QMessageBox.critical(
                self, "palimpsestr",
                "Calibrazione OxCal fallita.\n\nServono R con i pacchetti "
                "oxcAAR + palimpsestr e il motore OxCal (oxcAAR::quickSetupOxcal "
                "lo scarica; richiede Java e rete al primo uso).\n\n%s" % msg)
            return None
        out = {}
        with open(sout, encoding="utf-8") as f:
            for row in csv.DictReader(f):
                try:
                    out[row["id"]] = (int(float(row["start"])),
                                      int(float(row["end"])))
                except (KeyError, ValueError):
                    continue
        return out

    def _calibrate_and_save(self):
        rows_in = self._collect_rows(require_c14=True)
        if rows_in is None:
            return
        if not rows_in:
            QMessageBox.warning(self, "palimpsestr",
                                "Aggiungi almeno una riga con data C14.")
            return
        samples = [{"id": str(i), "c14_bp": r["c14_bp"], "c14_error": r["c14_error"]}
                   for i, r in enumerate(rows_in)]
        self.status.setText(
            "Calibrazione di %d campione/i con OxCal… (il primo avvio "
            "scarica OxCal)" % len(samples))
        try:
            from qgis.PyQt.QtWidgets import QApplication
            QApplication.processEvents()
        except Exception:
            pass
        cal = self._calibrate(samples)
        if cal is None:
            self.status.setText("")
            return
        save = []
        for i, r in enumerate(rows_in):
            se = cal.get(str(i))
            if not se:
                continue
            save.append((r["sito"], r["area"], r["us"], se[0], se[1],
                         r["lab_code"], "oxcal"))
        n = self._save_rows(save)
        self.status.setText("Salvate %d data/e US calibrate in %s."
                            % (n, CHRONOLOGY_TABLE))
        if n:
            QMessageBox.information(
                self, "palimpsestr",
                "Salvate %d data/e calibrate in %s." % (n, CHRONOLOGY_TABLE))

    # --------------------------------------------------------------- import ---
    def _import_samples_csv(self):
        import csv
        fn, _ = QFileDialog.getOpenFileName(
            self, "Importa campioni C14 (CSV)", self.p.HOME, "CSV (*.csv)")
        if not fn:
            return
        try:
            with open(fn, encoding="utf-8-sig", newline="") as f:
                rd = csv.DictReader(f)
                cols = {c.lower().strip(): c for c in (rd.fieldnames or [])}

                def g(row, *keys):
                    for k in keys:
                        if k in cols:
                            return (row.get(cols[k]) or "").strip()
                    return ""
                for row in rd:
                    self._add_row(g(row, "sito"), g(row, "area"), g(row, "us"),
                                  g(row, "c14_bp", "bp"),
                                  g(row, "c14_error", "error", "std"),
                                  g(row, "lab_code", "lab"))
        except Exception as e:
            QMessageBox.critical(self, "palimpsestr",
                                 "Impossibile leggere il CSV:\n%s" % e)

    def _import_calibrated_csv(self):
        import csv
        fn, _ = QFileDialog.getOpenFileName(
            self, "Importa range calibrati (CSV)", self.p.HOME, "CSV (*.csv)")
        if not fn:
            return
        save = []
        try:
            with open(fn, encoding="utf-8-sig", newline="") as f:
                rd = csv.DictReader(f)
                cols = {c.lower().strip(): c for c in (rd.fieldnames or [])}
                if not all(k in cols for k in ("sito", "us", "start", "end")):
                    QMessageBox.warning(
                        self, "palimpsestr",
                        "Il CSV deve avere almeno le colonne: sito, us, start, "
                        "end (opzionali: area, lab_code, source).")
                    return

                def g(row, k):
                    return (row.get(cols[k]) or "").strip() if k in cols else ""
                for row in rd:
                    sito, us = g(row, "sito"), g(row, "us")
                    if not sito or not us:
                        continue
                    try:
                        save.append((sito, g(row, "area") or None, int(us),
                                     int(float(g(row, "start"))),
                                     int(float(g(row, "end"))),
                                     g(row, "lab_code") or None,
                                     g(row, "source") or "import"))
                    except ValueError:
                        continue
        except Exception as e:
            QMessageBox.critical(self, "palimpsestr",
                                 "Impossibile leggere il CSV:\n%s" % e)
            return
        if not save:
            QMessageBox.warning(self, "palimpsestr",
                                "Nessuna riga valida trovata nel CSV.")
            return
        n = self._save_rows(save)
        self.status.setText("Importate %d data/e US calibrate." % n)
        if n:
            QMessageBox.information(
                self, "palimpsestr",
                "Importate %d data/e calibrate in %s." % (n, CHRONOLOGY_TABLE))


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
