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
plot_png <- if (length(args) >= 3) args[3] else ""
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
res <- res[match(ids, as.character(res$id)), ]
if (nzchar(plot_png)) {
  # Rich, descriptive per-US panels: shaded posterior probability curve over
  # the calendar axis, 95% HPD interval marked, BP +/- error in the title.
  tryCatch({
    nC <- length(cal)
    fmt_yr <- function(y) {
      y <- as.integer(round(y))
      if (y < 0) sprintf("%d a.C.", -y) else sprintf("%d d.C.", y)
    }
    grDevices::png(plot_png, width = 1200,
                   height = max(460L, 270L * nC), res = 130)
    op <- graphics::par(mfrow = c(nC, 1), mar = c(4.2, 4.4, 3.6, 1.0))
    on.exit(graphics::par(op), add = TRUE)
    for (i in seq_len(nC)) {
      g <- cal[[i]]$raw_probabilities
      x <- as.numeric(g$dates); y <- as.numeric(g$probabilities)
      keep <- is.finite(x) & is.finite(y)
      x <- x[keep]; y <- y[keep]
      if (!length(x)) { graphics::plot.new(); next }
      o <- order(x); x <- x[o]; y <- y[o]
      lo <- res$date_min[i]; hi <- res$date_max[i]
      graphics::plot(x, y, type = "n",
        xlab = "anni calendariali (negativo = a.C.)", ylab = "probabilita",
        main = sprintf("US %s  -  %s ± %s BP\n95%% HPD: %s - %s",
                       ids[i], s$c14_bp[i], s$c14_error[i],
                       fmt_yr(lo), fmt_yr(hi)),
        cex.main = 0.95)
      graphics::rect(lo, graphics::par("usr")[3], hi, graphics::par("usr")[4],
                     col = grDevices::adjustcolor("steelblue", 0.16), border = NA)
      graphics::polygon(c(x[1], x, x[length(x)]), c(0, y, 0),
                        col = grDevices::adjustcolor("grey50", 0.55), border = NA)
      graphics::lines(x, y, col = "grey25")
      graphics::abline(v = c(lo, hi), col = "firebrick", lty = 2, lwd = 1.4)
    }
    grDevices::dev.off()
  }, error = function(e) {})
}
out <- data.frame(id = as.character(res$id),
                  start = as.integer(round(res$date_min)),
                  end   = as.integer(round(res$date_max)),
                  stringsAsFactors = FALSE)
write.csv(out, out_csv, row.names = FALSE)
cat("calibrated ", nrow(out), " sample(s)\n", sep = "")
"""

# Driver for the AI report: fits the SEF model once and writes the *facts* the
# AI agents need — per-phase summary, per-class composition, per-US diagnostics,
# the absolute-chronology rows, the gg_* diagnostic figures (always produced,
# unlike export_sef_report which embeds them in the PDF/DOCX), and the R
# interpretive narrative (.md). Args: db, is_pg(0/1), site, K, class_model,
# noise(0/1), source, out_dir.
SEF_FACTS_R = r"""args <- commandArgs(trailingOnly = TRUE)
db_arg <- args[1]; is_pg <- args[2] == "1"; site_arg <- args[3]
K <- as.integer(args[4]); class_model <- args[5]; use_noise <- args[6] == "1"
source_sel <- args[7]; out_dir <- args[8]
suppressMessages({ library(palimpsestr); library(sf); library(DBI); library(ggplot2) })
if (is_pg) {
  con  <- DBI::dbConnect(RPostgres::Postgres(), dbname = db_arg)
  geom <- tryCatch(sf::st_read(con, query = "SELECT us_s, the_geom FROM pyunitastratigrafiche", quiet = TRUE),
                   error = function(e) NULL)
} else {
  con  <- DBI::dbConnect(RSQLite::SQLite(), db_arg)
  geom <- tryCatch(sf::st_read(db_arg, layer = "pyunitastratigrafiche", quiet = TRUE),
                   error = function(e) NULL)
}
site <- if (nchar(site_arg) > 0 && site_arg != "all") site_arg else NULL
d <- read_pyarchinit(con, us_geometry = geom, sito = site, source = source_sel)
chrono <- tryCatch({
  if ("palimpsest_chronology" %in% DBI::dbListTables(con)) {
    cols <- DBI::dbListFields(con, "palimpsest_chronology")
    sel <- if ("taf" %in% cols)
      'sito, area, us, "start", "end", taf, lab_code, source'
    else 'sito, area, us, "start", "end", lab_code, source'
    DBI::dbGetQuery(con, paste0("SELECT ", sel, " FROM palimpsest_chronology"))
  } else data.frame()
}, error = function(e) data.frame())
DBI::dbDisconnect(con)
if (!is.null(site) && nrow(chrono)) chrono <- chrono[chrono$sito == site, , drop = FALSE]
if (nrow(chrono) && !("taf" %in% names(chrono))) chrono$taf <- NA_real_
write.csv(chrono, file.path(out_dir, "chronology.csv"), row.names = FALSE)

# Apply the per-US taphonomic score (taf) from palimpsest_chronology, if any,
# so fit_sef down-weights redeposited/disturbed units. Finds without a taf row
# keep read_pyarchinit's default weight.
if (nrow(chrono) && "taf" %in% names(chrono) && "context" %in% names(d) &&
    "taf_score" %in% names(d)) {
  tm <- chrono[!is.na(chrono$taf), ]
  if (nrow(tm)) {
    taf_map <- stats::setNames(as.numeric(tm$taf), as.character(tm$us))
    hit <- as.character(d$context) %in% names(taf_map)
    if (any(hit)) d$taf_score[hit] <- taf_map[as.character(d$context)[hit]]
  }
}

fit <- reorder_phases(fit_sef(d, k = K, context = "context",
                              tafonomy = "taf_score", class_model = class_model,
                              noise = use_noise))

pts <- as_sf_phase(fit, crs = NA_integer_)
df  <- sf::st_drop_geometry(pts)
agg <- do.call(rbind, lapply(split(df, df$dominant_phase), function(g) data.frame(
  phase = g$dominant_phase[1], n_finds = nrow(g),
  mean_date = round(mean((g$date_min + g$date_max) / 2, na.rm = TRUE)),
  n_us = length(unique(g$context)), stringsAsFactors = FALSE)))
agg$pct <- round(100 * agg$n_finds / sum(agg$n_finds), 1)
write.csv(agg, file.path(out_dir, "phase_summary.csv"), row.names = FALSE)
write.csv(as_phase_table(fit), file.path(out_dir, "diagnostics.csv"), row.names = FALSE)
if ("class" %in% names(df)) {
  comp <- as.data.frame(table(phase = df$dominant_phase, class = df$class))
  comp <- comp[comp$Freq > 0, ]
  write.csv(comp, file.path(out_dir, "composition.csv"), row.names = FALSE)
}

figdir <- file.path(out_dir, "figs"); dir.create(figdir, showWarnings = FALSE)
save_gg <- function(name, fn) tryCatch({
  p <- fn(fit)
  if (inherits(p, "ggplot"))
    ggplot2::ggsave(file.path(figdir, paste0(name, ".png")), p,
                    width = 8, height = 5, dpi = 130)
}, error = function(e) {})
save_gg("phasefield", gg_phasefield)
save_gg("phase_composition", gg_phase_composition)
save_gg("entropy", gg_entropy)
save_gg("energy", gg_energy)
save_gg("intrusions", gg_intrusions)
save_gg("direction", gg_direction)
save_gg("outliers", gg_outliers)
save_gg("unit_coherence", gg_unit_coherence)

tryCatch(export_sef_report(fit, file.path(out_dir, "sef_report.pdf"),
                           format = "docx", lang = "it", site = site),
         error = function(e) {})
cat("facts ready: ", nrow(agg), " phases, ", nrow(chrono), " chronology rows, ",
    length(list.files(figdir, pattern = "png$")), " figures\n", sep = "")
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
        return exe

    def _gather_sef_facts(self):
        """Fit SEF (R) and collect facts for the AI agents (figures, per-phase
        summary, composition, diagnostics, chronology, narrative), or None."""
        import tempfile, subprocess, csv
        dsn = self._pg_dsn()
        if dsn:
            db_arg, is_pg = dsn, "1"
        else:
            path = self._require_sqlite()
            if not path:
                return None
            db_arg, is_pg = path, "0"
        self._augment_render_env()
        out_dir = tempfile.mkdtemp(prefix="palimpsestr_ai_")
        rdrv = os.path.join(out_dir, "sef_facts.R")
        with open(rdrv, "w", encoding="utf-8") as f:
            f.write(SEF_FACTS_R)
        args = [self._find_rscript(), rdrv, db_arg, is_pg, self._site(),
                str(self.spin_k.value()),
                ["multinomial", "gaussian"][self.combo_model.currentIndex()],
                "1" if self.check_noise.isChecked() else "0",
                ["both", "materials", "pottery"][self.combo_source.currentIndex()],
                out_dir]
        from qgis.PyQt.QtWidgets import QApplication
        from qgis.PyQt.QtCore import Qt
        QApplication.setOverrideCursor(Qt.WaitCursor)
        try:
            proc = subprocess.run(args, capture_output=True, text=True,
                                  timeout=3600)
        except Exception as e:
            QApplication.restoreOverrideCursor()
            QMessageBox.critical(self, "palimpsestr",
                                 "Impossibile eseguire R (Rscript):\n%s" % e)
            return None
        finally:
            QApplication.restoreOverrideCursor()
        if proc.returncode != 0:
            QMessageBox.critical(
                self, "palimpsestr", "Analisi SEF (R) fallita:\n\n%s"
                % ((proc.stderr or proc.stdout or "")[-2000:]))
            return None

        def _read_csv(name):
            p = os.path.join(out_dir, name)
            if not os.path.exists(p):
                return []
            with open(p, encoding="utf-8-sig", newline="") as fh:
                return list(csv.DictReader(fh))

        md = os.path.join(out_dir, "sef_report.md")
        r_markdown = ""
        if os.path.exists(md):
            with open(md, encoding="utf-8") as fh:
                r_markdown = fh.read()
        figs_dir = os.path.join(out_dir, "figs")
        figures = []
        if os.path.isdir(figs_dir):
            figures = sorted(os.path.splitext(f)[0]
                             for f in os.listdir(figs_dir) if f.endswith(".png"))
        from .palimpsest_ai_report import _model_name, _source_name
        return {
            "site": self._site(),
            "backend": "PostgreSQL/PostGIS" if dsn else "SQLite/Spatialite",
            "k": self.spin_k.value(),
            "class_model": _model_name(self.combo_model.currentIndex()),
            "noise": self.check_noise.isChecked(),
            "threshold": self.spin_thr.value(),
            "source": _source_name(self.combo_source.currentIndex()),
            "has_chronology": self._has_chronology(),
            "r_markdown": r_markdown,
            "phase_summary": _read_csv("phase_summary.csv"),
            "composition": _read_csv("composition.csv"),
            "diagnostics": _read_csv("diagnostics.csv"),
            "chronology": _read_csv("chronology.csv"),
            "figures": figures,
            "figures_dir": figs_dir,
        }

    def open_ai_report(self):
        if not (self._pg_dsn() or self._sqlite_path()):
            QMessageBox.warning(
                self, "palimpsestr",
                "Nessuna connessione al database attiva.\n\n"
                "Connetti un database pyArchInit (SQLite o PostgreSQL).")
            return
        facts = self._gather_sef_facts()
        if facts is None:
            return
        if not facts.get("phase_summary") and not facts.get("r_markdown"):
            QMessageBox.warning(
                self, "palimpsestr",
                "L'analisi SEF non ha prodotto risultati leggibili "
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
            "Cronologia & tafonomia per US (tabella <b>palimpsest_chronology</b>, "
            "usata da palimpsestr al posto della datazione testuale).<br>"
            "All'apertura vengono <b>caricate tutte le US del sito</b> con "
            "<b>Periodo</b> e <b>n. reperti</b> (colonne informative): assegna il "
            "<b>taf [0-1]</b> a ogni US e, dove hai una data, le colonne OxCal. "
            "Modifica <b>start/end/taf</b> e premi <b>Salva modifiche</b>; per "
            "nuove date inserisci <b>C14 BP ± errore</b> e premi <b>Calibra e "
            "salva</b>. Vengono salvate solo le US con taf e/o data."))

        # Cols: Sito, Area, US, Periodo(RO), N.rep(RO), taf, C14 BP, ± err,
        #       start, end, Lab code, source
        self.table = QTableWidget(0, 12)
        self.table.setHorizontalHeaderLabels(
            ["Sito", "Area", "US", "Periodo", "N. rep.", "taf [0-1]",
             "C14 BP", "± errore", "start (cal)", "end (cal)", "Lab code",
             "source"])
        self.table.horizontalHeader().setSectionResizeMode(_stretch_mode())
        lay.addWidget(self.table)

        row1 = QHBoxLayout()
        b_add = QPushButton("Aggiungi riga")
        b_add.clicked.connect(lambda: self._add_row())
        b_del = QPushButton("Rimuovi riga")
        b_del.clicked.connect(self._remove_row)
        b_reload = QPushButton("Ricarica dal DB")
        b_reload.clicked.connect(self._load_existing)
        b_imps = QPushButton("Importa campioni CSV…")
        b_imps.clicked.connect(self._import_samples_csv)
        row1.addWidget(b_add); row1.addWidget(b_del)
        row1.addWidget(b_reload); row1.addWidget(b_imps)
        lay.addLayout(row1)

        row2 = QHBoxLayout()
        b_ddl = QPushButton("Crea/aggiorna tabella")
        b_ddl.clicked.connect(self._create_table)
        b_cal = QPushButton("Calibra e salva (OxCal)")
        b_cal.clicked.connect(self._calibrate_and_save)
        b_edit = QPushButton("Salva modifiche (start/end)")
        b_edit.clicked.connect(self._save_edits)
        b_impc = QPushButton("Importa range calibrati (CSV)…")
        b_impc.clicked.connect(self._import_calibrated_csv)
        b_close = QPushButton("Chiudi")
        b_close.clicked.connect(self.accept)
        row2.addWidget(b_ddl); row2.addWidget(b_cal)
        row2.addWidget(b_edit); row2.addWidget(b_impc); row2.addWidget(b_close)
        lay.addLayout(row2)

        # OxCal calibration plot (filled after "Calibra e salva").
        self._last_plot = None
        row3 = QHBoxLayout()
        self.btn_show_plot = QPushButton("Mostra grafico OxCal")
        self.btn_show_plot.clicked.connect(self._show_plot)
        self.btn_show_plot.setEnabled(False)
        self.btn_save_plot = QPushButton("Esporta grafico (PNG)…")
        self.btn_save_plot.clicked.connect(self._save_plot)
        self.btn_save_plot.setEnabled(False)
        row3.addWidget(self.btn_show_plot)
        row3.addWidget(self.btn_save_plot)
        row3.addStretch()
        lay.addLayout(row3)

        self.status = QLabel("")
        self.status.setWordWrap(True)
        lay.addWidget(self.status)

        self._load_existing()

    # --------------------------------------------------------------- table ---
    def _add_row(self, sito="", area="", us="", periodo="", nrep="", taf="",
                 bp="", err="", start="", end="", lab="", source=""):
        from qgis.PyQt.QtCore import Qt
        r = self.table.rowCount()
        self.table.insertRow(r)
        cells = [sito, area, us, periodo, nrep, taf, bp, err, start, end,
                 lab, source]
        for c, v in enumerate(cells):
            it = QTableWidgetItem("" if v is None else str(v))
            if c in (3, 4):  # Periodo / N. rep. are read-only info columns
                it.setFlags(it.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(r, c, it)

    def _remove_row(self):
        rows = sorted({i.row() for i in self.table.selectedIndexes()}, reverse=True)
        for r in rows:
            self.table.removeRow(r)

    @staticmethod
    def _periodo_str(pi, fi, pf, ff):
        a = ("%s/%s" % (pi or "", fi or "")).strip("/")
        b = ("%s/%s" % (pf or "", ff or "")).strip("/")
        if a and b and a != b:
            return "%s–%s" % (a, b)
        return a or b or ""

    def _load_existing(self):
        """Seed the table with ALL US of the site (Periodo + n. finds, read-only)
        and merge any saved palimpsest_chronology values (taf, start/end, ...)."""
        self.table.setRowCount(0)
        site = self.p.edit_site.text().strip()
        site_f = site if site and site != "all" else None
        us_rows, counts, chrono = [], {}, {}
        try:
            dsn = self.p._pg_dsn()
            kind = None
            if dsn:
                import psycopg2
                conn = psycopg2.connect(dsn); ph = "%s"; kind = "pg"
            else:
                path = self.p._sqlite_path()
                conn = None
                if path and os.path.exists(path):
                    import sqlite3
                    conn = sqlite3.connect(path); ph = "?"; kind = "sqlite"
            if conn is not None:
                try:
                    self._ddl(conn, kind)  # ensure the taf column exists
                    cur = conn.cursor()
                    # saved chronology/taf
                    cq = ('SELECT sito, area, us, "start", "end", taf, lab_code, '
                          'source FROM %s' % CHRONOLOGY_TABLE)
                    cp = ()
                    if site_f:
                        cq += " WHERE sito = " + ph; cp = (site_f,)
                    cur.execute(cq, cp)
                    for r in cur.fetchall():
                        chrono[(r[0], str(r[2]))] = r[3:]  # start,end,taf,lab,source
                    # all US of the site
                    uq = ("SELECT sito, area, us, periodo_iniziale, fase_iniziale, "
                          "periodo_finale, fase_finale FROM us_table")
                    up = ()
                    if site_f:
                        uq += " WHERE sito = " + ph; up = (site_f,)
                    uq += " ORDER BY CAST(us AS INTEGER)"
                    cur.execute(uq, up)
                    us_rows = cur.fetchall()
                    # material counts per (sito, us)
                    for tbl in ("inventario_materiali_table", "pottery_table"):
                        try:
                            mq = "SELECT sito, us, COUNT(*) FROM %s" % tbl
                            mp = ()
                            if site_f:
                                mq += " WHERE sito = " + ph; mp = (site_f,)
                            mq += " GROUP BY sito, us"
                            cur.execute(mq, mp)
                            for (s, u, n) in cur.fetchall():
                                counts[(s, str(u))] = counts.get((s, str(u)), 0) + n
                        except Exception:
                            pass
                except Exception:
                    us_rows = []
                finally:
                    conn.close()
        except Exception:
            us_rows = []

        n_chr = 0
        for r in us_rows:
            sito, area, us = r[0], r[1], r[2]
            periodo = self._periodo_str(r[3], r[4], r[5], r[6])
            nrep = counts.get((sito, str(us)), 0)
            ch = chrono.get((sito, str(us)))
            if ch:
                st, en, taf, lab, src = ch
                n_chr += 1
            else:
                st = en = taf = lab = src = ""
            self._add_row(sito, area, us, periodo, nrep, taf, "", "",
                          st, en, lab, src)
        if self.table.rowCount() == 0:
            self._add_row(site_f or "")
        else:
            self.status.setText("Caricate %d US (%d con cronologia/taf)."
                                % (len(us_rows), n_chr))

    def _collect_rows(self, require_c14):
        """Read the table into dicts; show a message and return None on error.

        require_c14=True  -> needs C14 BP/error (for calibration)
        require_c14=False -> needs start/end    (direct edit/save)
        Each dict carries ``_row`` (the table row index).
        """
        rows = []
        for r in range(self.table.rowCount()):
            def cell(c):
                it = self.table.item(r, c)
                return it.text().strip() if it and it.text() else ""
            sito, area, us = cell(0), cell(1) or None, cell(2)
            taf = cell(5)
            bp, err = cell(6), cell(7)
            start, end = cell(8), cell(9)
            lab, source = cell(10) or None, cell(11) or None
            # Only process rows the user actually filled for this action:
            # calibration needs C14; a direct save needs taf and/or a date.
            if require_c14:
                if not (bp or err):
                    continue
            elif not (taf or start or end):
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
            taf_val = None
            if taf:
                try:
                    taf_val = float(taf)
                except ValueError:
                    QMessageBox.warning(self, "palimpsestr",
                                        "Riga %d: taf dev'essere un numero in "
                                        "[0,1]." % (r + 1))
                    return None
                if not (0.0 <= taf_val <= 1.0):
                    QMessageBox.warning(self, "palimpsestr",
                                        "Riga %d: taf dev'essere tra 0 e 1."
                                        % (r + 1))
                    return None
            rec = {"_row": r, "sito": sito, "area": area, "us": us_i,
                   "taf": taf_val, "lab_code": lab, "source": source}
            if require_c14:
                try:
                    rec["c14_bp"] = float(bp)
                    rec["c14_error"] = float(err)
                except ValueError:
                    QMessageBox.warning(
                        self, "palimpsestr",
                        "Riga %d: C14 BP ed errore devono essere numeri." % (r + 1))
                    return None
            else:
                # start/end optional in direct-save mode (a US may carry only a
                # taf value, with no absolute date).
                if start or end:
                    try:
                        rec["start"] = int(float(start))
                        rec["end"] = int(float(end))
                    except ValueError:
                        QMessageBox.warning(
                            self, "palimpsestr",
                            "Riga %d: start ed end devono essere interi." % (r + 1))
                        return None
                else:
                    rec["start"] = None
                    rec["end"] = None
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
        # taf = taphonomic score in [0,1] (per US), optional.
        cur = conn.cursor()
        cur.execute(
            'CREATE TABLE IF NOT EXISTS %s ('
            ' id %s, sito TEXT, area TEXT, us INTEGER,'
            ' "start" INTEGER, "end" INTEGER, taf REAL, lab_code TEXT,'
            ' source TEXT)' % (CHRONOLOGY_TABLE, pk))
        # Migrate older tables that predate the taf column.
        try:
            cur.execute("ALTER TABLE %s ADD COLUMN taf REAL" % CHRONOLOGY_TABLE)
        except Exception:
            try:
                conn.rollback()
            except Exception:
                pass
        conn.commit()

    def _save_rows(self, rows):
        """Upsert (sito,area,us)-keyed rows; returns the count written."""
        conn, kind, ph = self._conn()
        if conn is None:
            return 0
        try:
            self._ddl(conn, kind)
            cur = conn.cursor()
            for (sito, area, us, start, end, taf, lab, source) in rows:
                cur.execute(
                    "DELETE FROM %s WHERE sito = %s AND us = %s "
                    "AND COALESCE(area,'') = COALESCE(%s,'')"
                    % (CHRONOLOGY_TABLE, ph, ph, ph), (sito, us, area))
                cur.execute(
                    'INSERT INTO %s (sito, area, us, "start", "end", taf, '
                    'lab_code, source) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)'
                    % (CHRONOLOGY_TABLE, ph, ph, ph, ph, ph, ph, ph, ph),
                    (sito, area, us, start, end, taf, lab, source))
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
        splot = os.path.join(d, "oxcal_plot.png")
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
            proc = subprocess.run([rscript, rdrv, sin, sout, splot],
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
        self._last_plot = splot if os.path.exists(splot) else None
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
        self._last_plot = None
        cal = self._calibrate(samples)
        if cal is None:
            self.status.setText("")
            return
        has_plot = bool(self._last_plot)
        self.btn_show_plot.setEnabled(has_plot)
        self.btn_save_plot.setEnabled(has_plot)
        save = []
        for i, r in enumerate(rows_in):
            se = cal.get(str(i))
            if not se:
                continue
            # write the calibrated start/end back into the table (cols 8,9)
            self.table.setItem(r["_row"], 8, QTableWidgetItem(str(se[0])))
            self.table.setItem(r["_row"], 9, QTableWidgetItem(str(se[1])))
            self.table.setItem(r["_row"], 11, QTableWidgetItem("oxcal"))
            save.append((r["sito"], r["area"], r["us"], se[0], se[1],
                         r["taf"], r["lab_code"], "oxcal"))
        n = self._save_rows(save)
        if n:
            self._load_existing()
            self.status.setText("Salvate %d data/e US calibrate in %s."
                                % (n, CHRONOLOGY_TABLE))
            QMessageBox.information(
                self, "palimpsestr",
                "Salvate %d data/e calibrate in %s." % (n, CHRONOLOGY_TABLE))

    def _save_edits(self):
        """Save the table's start/end directly (manual edit, no calibration)."""
        rows_in = self._collect_rows(require_c14=False)
        if rows_in is None:
            return
        if not rows_in:
            QMessageBox.warning(self, "palimpsestr",
                                "Inserisci almeno una riga con start/end.")
            return
        save = [(r["sito"], r["area"], r["us"], r["start"], r["end"],
                 r["taf"], r["lab_code"], r["source"] or "manual")
                for r in rows_in]
        n = self._save_rows(save)
        if n:
            self._load_existing()
            self.status.setText("Salvate/aggiornate %d date in %s."
                                % (n, CHRONOLOGY_TABLE))
            QMessageBox.information(
                self, "palimpsestr",
                "Salvate/aggiornate %d date in %s." % (n, CHRONOLOGY_TABLE))

    # ----------------------------------------------------------- OxCal plot ---
    def _show_plot(self):
        if self._last_plot and os.path.exists(self._last_plot):
            self.p._open(self._last_plot)
        else:
            QMessageBox.information(self, "palimpsestr",
                                    "Nessun grafico disponibile. Esegui prima "
                                    "una calibrazione OxCal.")

    def _save_plot(self):
        if not (self._last_plot and os.path.exists(self._last_plot)):
            return
        fn, _ = QFileDialog.getSaveFileName(
            self, "Esporta grafico OxCal (PNG)",
            os.path.join(self.p.HOME, "oxcal_calibration.png"), "PNG (*.png)")
        if not fn:
            return
        if not fn.lower().endswith(".png"):
            fn += ".png"
        try:
            import shutil
            shutil.copyfile(self._last_plot, fn)
        except Exception as e:
            QMessageBox.critical(self, "palimpsestr",
                                 "Esportazione fallita:\n%s" % e)
            return
        self.status.setText("Grafico esportato: %s" % fn)

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
                    self._add_row(
                        g(row, "sito"), g(row, "area"), g(row, "us"),
                        "", "",  # Periodo / N.rep (info, not in a samples CSV)
                        g(row, "taf"),
                        g(row, "c14_bp", "bp"),
                        g(row, "c14_error", "error", "std"),
                        g(row, "start"), g(row, "end"),
                        g(row, "lab_code", "lab"), g(row, "source"))
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
                    taf_s = g(row, "taf")
                    try:
                        save.append((sito, g(row, "area") or None, int(us),
                                     int(float(g(row, "start"))),
                                     int(float(g(row, "end"))),
                                     float(taf_s) if taf_s else None,
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
        if n:
            self._load_existing()
            self.status.setText("Importate %d data/e US calibrate." % n)
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
