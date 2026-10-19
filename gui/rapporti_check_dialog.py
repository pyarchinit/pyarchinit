"""Verifica rapporti stratigrafici — Qt panel + dialog.

UI over ``modules.utility.rapporti_check``: pick a site, run the
s3dgraphy-backed validators (cycles / self-loops / connection legality /
reciprocity), preview the conservative fixes, apply them (snapshot-protected)
and roll back. See docs/superpowers/specs/2026-06-06-rapporti-validation-autofix-design.md.

``RapportiCheckPanel`` is a reusable ``QWidget`` (embedded as a tab in the
s3dgraphy import dialog); ``RapportiCheckDialog`` is a thin standalone wrapper.
"""
from __future__ import annotations

from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtWidgets import (
    QCheckBox, QDialog, QWidget, QVBoxLayout, QHBoxLayout, QComboBox,
    QPushButton, QTreeWidget, QTreeWidgetItem, QTextEdit, QLabel,
    QMessageBox, QSplitter,
)

from modules.utility import rapporti_check as RC
from modules.utility.pyarchinit_home import pyarchinit_home

_USER_ROLE = int(Qt.UserRole)


def _qgis_lang():
    """Current QGIS UI language (2-letter), defaulting to Italian."""
    try:
        from qgis.core import QgsSettings
        return (QgsSettings().value("locale/userLocale", "it", type=str)
                or "it")[:2]
    except Exception:
        return "it"


class RapportiCheckPanel(QWidget):
    """Site picker → report → preview → apply / rollback.

    ``db_provider`` (optional): a zero-arg callable returning a backend
    ``DbHandle``. When omitted the panel resolves the active pyArchInit
    project connection itself (standalone use). The import dialog passes
    its own ``db_manager`` so the verifica runs against the same DB it
    just imported into.
    """

    def __init__(self, iface=None, parent=None, db_provider=None):
        super().__init__(parent)
        self.iface = iface
        self._db_provider = db_provider
        self._lang = _qgis_lang()
        self._report = None
        self._token = None
        self._chrono_bounds = {}
        self._chrono_errore = None
        self._sites_failed = False
        self._sites_loaded = False
        self._build_ui()
        # I siti si leggono quando la scheda si apre (showEvent), non qui: la
        # finestra Extended Matrix si apre sulla scheda Import, e con un
        # server che non risponde ogni tentativo tiene QGIS fermo.

    # -- db plumbing (backend-agnostic) ------------------------------------
    def _handle(self):
        if self._db_provider is not None:
            from s3dgraphy.sync._db_handle import _resolve_db_handle
            db = self._db_provider()
            if db is None:
                raise LookupError("nessun database collegato")
            return _resolve_db_handle(db)
        from modules.db.pyarchinit_conn_strings import Connection
        from modules.db.pyarchinit_db_manager import get_db_manager
        from s3dgraphy.sync._db_handle import _resolve_db_handle
        conn_str = Connection().conn_str()
        db_manager = get_db_manager(conn_str, use_singleton=True)
        return _resolve_db_handle(db_manager)

    # -- UI -----------------------------------------------------------------
    def _build_ui(self):
        lay = QVBoxLayout(self)
        top = QHBoxLayout()
        top.addWidget(QLabel("Sito:"))
        self.cboSite = QComboBox()
        top.addWidget(self.cboSite, 1)
        self.btnRun = QPushButton("Esegui verifica")
        self.btnRun.clicked.connect(self._run)
        top.addWidget(self.btnRun)
        self.btnContinuity = QPushButton("Genera continuità")
        self.btnContinuity.setToolTip(
            "Crea/aggiorna le schede CON per le US/USM che attraversano "
            "più periodi (periodo iniziale ≠ finale).")
        self.btnContinuity.clicked.connect(self._run_genera_continuita)
        top.addWidget(self.btnContinuity)
        # Di suo la continuità guarda il **periodo**, e una muratura che
        # va da 2/3 a 2/4 non genera niente: stesso periodo, cambia solo
        # la fase. Per chi scava è una sopravvivenza come le altre, ma
        # non si accende da sé — questo bottone è già nelle mani di
        # qualcuno, e un automatismo che cambia idea da solo scrive nel
        # database cose che nessuno ha chiesto.
        self.chkPhases = QCheckBox("anche i salti di fase")
        self.chkPhases.setToolTip(
            "Spenta, la continuità nasce solo quando il periodo iniziale è "
            "diverso dal finale.\nAccesa, conta anche il salto di fase "
            "dentro lo stesso periodo (2/3 → 2/4): servono entrambe le "
            "fasi.\nUn'unità che non si muove — stesso periodo e stessa "
            "fase — non è mai una continuità.")
        top.addWidget(self.chkPhases)
        lay.addLayout(top)
        # Senza database lo si dice qui, non con un avviso modale (vedi _load_sites).
        stato = QHBoxLayout()
        self.lblStato = QLabel("")
        self.lblStato.setWordWrap(True)
        self.lblStato.setHidden(True)
        stato.addWidget(self.lblStato, 1)
        self.btnRiprova = QPushButton("Riprova")
        self.btnRiprova.setHidden(True)
        self.btnRiprova.clicked.connect(self._load_sites)
        stato.addWidget(self.btnRiprova)
        lay.addLayout(stato)

        split = QSplitter(Qt.Vertical)
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Problema"])
        self.tree.itemSelectionChanged.connect(self._preview)
        split.addWidget(self.tree)
        self.preview = QTextEdit()
        self.preview.setReadOnly(True)
        split.addWidget(self.preview)
        split.setSizes([420, 200])
        lay.addWidget(split, 1)

        self.lblSummary = QLabel("")
        lay.addWidget(self.lblSummary)

        btns = QHBoxLayout()
        btns.addStretch(1)
        self.btnRollback = QPushButton("Annulla ultimo fix")
        self.btnRollback.clicked.connect(self._rollback)
        self.btnRollback.setEnabled(False)
        btns.addWidget(self.btnRollback)
        self.btnApply = QPushButton("Applica fix selezionati")
        self.btnApply.clicked.connect(self._apply)
        btns.addWidget(self.btnApply)
        lay.addLayout(btns)

    def _load_sites(self):
        """I siti del database nel selettore; True se si sono letti.

        Il pannello si costruisce dentro la finestra Extended Matrix, prima
        che si veda: senza database (la finestra aperta senza, o un database
        che non risponde) un avviso modale si apriva da solo, davanti a una
        finestra che non c'era ancora. Ora lo dice qui dentro, spegne i
        pulsanti e riprova quando la scheda si apre o dopo un import."""
        try:
            from sqlalchemy import text
            handle = self._handle()
            with handle.engine.connect() as conn:
                rows = conn.execute(text(
                    "SELECT DISTINCT sito FROM us_table "
                    "WHERE sito IS NOT NULL AND sito <> '' ORDER BY sito")
                ).fetchall()
        except Exception as exc:
            self._sites_failed = True
            if isinstance(exc, LookupError):
                testo = RC._t(self._lang, "m_no_database")
            else:                       # c'è, ma non risponde o non è di pyArchInit
                dettaglio = (str(exc).strip().splitlines() or [type(exc).__name__])[0][:200]
                testo = RC._t(self._lang, "m_db_unreadable").format(errore=dettaglio)
            self.lblStato.setText(testo)
            self.lblStato.setToolTip(str(exc))
            self.lblStato.setHidden(False)
            self.btnRiprova.setHidden(False)
            for b in (self.btnRun, self.btnContinuity, self.btnApply):
                b.setEnabled(False)
            return False
        self._sites_failed = False
        self._sites_loaded = True
        self.lblStato.setText("")
        self.lblStato.setToolTip("")
        self.lblStato.setHidden(True)
        self.btnRiprova.setHidden(True)
        scelto = self.cboSite.currentText()
        self.cboSite.clear()
        self.cboSite.addItems([str(r[0]) for r in rows])
        if scelto and self.cboSite.findText(scelto) >= 0:
            self.cboSite.setCurrentText(scelto)
        for b in (self.btnRun, self.btnContinuity, self.btnApply):
            b.setEnabled(True)
        return True

    def showEvent(self, event):
        """La prima volta che la scheda si apre, i siti. Dopo un errore non
        si riprova da soli (un server che non risponde terrebbe QGIS fermo a
        ogni apertura): c'è «Riprova»."""
        super().showEvent(event)
        if not self._sites_loaded and not self._sites_failed:
            self._load_sites()

    def select_sito(self, sito):
        """Pre-select *sito* in the picker (used by the import dialog to
        focus the verifica on the site just imported)."""
        if not sito:
            return
        if not self._sites_loaded:          # dopo un import il database risponde
            self._load_sites()
        idx = self.cboSite.findText(str(sito))
        if idx >= 0:
            self.cboSite.setCurrentIndex(idx)
        else:
            self.cboSite.addItem(str(sito))
            self.cboSite.setCurrentText(str(sito))

    # -- actions ------------------------------------------------------------
    def _run(self):
        sito = self.cboSite.currentText().strip()
        if not sito:
            return
        try:
            from modules.s3dgraphy.sync.graph_projector import GraphProjector
            from modules.utility import chronology_check as CC
            from modules.utility import temporal_check as TC
            handle = self._handle()
            graph = GraphProjector().populate_graph(handle, sito=sito)
            chrono = TC.build_chronology(handle, sito)
            unit_periods = TC.load_unit_periods(handle, sito)
            self._report = RC.check_rapporti(
                graph, sito=sito, lang=self._lang,
                chrono=chrono, unit_periods=unit_periods)
            # Gli avvisi cronologici sono altre categorie dello stesso albero:
            # _render raggruppa per `kind` e non ha bisogno di sapere da quale
            # verifica arrivano.
            self._chrono_bounds = {}
            self._chrono_errore = None
            try:
                periods, units = CC.load_chronology_rows(handle, sito)
                # La cronologia calcolata, per la provenienza nell'anteprima.
                # Si chiede **prima** di aggiungere gli avvisi: se inciampasse
                # dopo, la finestra mostrerebbe gli avvisi e insieme direbbe
                # che la verifica non è stata eseguita.
                self._chrono_bounds = CC.bounds_by_us(graph)
                self._report.issues.extend(CC.check_chronology(
                    periods, units, sito=sito, lang=self._lang))
            except Exception as exc:
                # Un inciampo della cronologia non porta via la verifica dei
                # rapporti, che ha già risposto: si dice e si va avanti.
                self._chrono_errore = str(exc)
        except Exception as exc:
            QMessageBox.critical(self, "pyArchInit", f"Verifica fallita: {exc}")
            return
        self._render()

    def _render(self):
        self.tree.clear()
        groups = {}
        for iss in self._report.issues:
            groups.setdefault(iss.kind, []).append(iss)
        n_auto = 0
        n_prop = 0
        for kind, issues in groups.items():
            title = RC.kind_title(kind, self._lang)
            top = QTreeWidgetItem([f"{title}  ({len(issues)})"])
            self.tree.addTopLevelItem(top)
            for iss in issues:
                child = QTreeWidgetItem([iss.summary])
                child.setData(0, _USER_ROLE, iss)
                if iss.edits:
                    # Spuntabile perché una correzione c'è; spuntata di suo
                    # solo se automatica. Una proposta — la fase da
                    # restringere, il rapporto da togliere a un ciclo — si
                    # applica solo se l'archeologo la spunta.
                    child.setCheckState(0, Qt.Checked if iss.auto
                                        else Qt.Unchecked)
                    if iss.auto:
                        n_auto += 1
                    else:
                        n_prop += 1
                top.addChild(child)
            top.setExpanded(True)
        total = len(self._report.issues)
        # «(selezionati)» rimanda alle spunte: con zero correzioni automatiche
        # non ce n'è nessuna, e la parentesi non dice niente.
        testo = ("%d problemi · %d correggibili automaticamente"
                 % (total, n_auto))
        if n_auto:
            testo += " (selezionati)"
        if n_prop:
            testo += " · %d proposte, da spuntare a mano" % n_prop
        testo += ". Anteprima un elemento per i dettagli."
        self.lblSummary.setText(testo)
        if self._chrono_errore:
            # Non si inghiotte in silenzio: la riga di riepilogo dice che gli
            # avvisi cronologici mancano, e perché.
            self.lblSummary.setText(
                self.lblSummary.text()
                + "  ⚠ verifica cronologia non eseguita: %s"
                % self._chrono_errore)
        self._token = None
        self.btnRollback.setEnabled(False)

    def _selected_issues(self):
        """Le issue spuntate che hanno una correzione: le automatiche sono
        spuntate di suo, le proposte solo se l'archeologo le ha spuntate."""
        out = []
        for i in range(self.tree.topLevelItemCount()):
            top = self.tree.topLevelItem(i)
            for j in range(top.childCount()):
                ch = top.child(j)
                iss = ch.data(0, _USER_ROLE)
                if (iss is not None and iss.edits
                        and ch.checkState(0) == Qt.Checked):
                    out.append(iss)
        return out

    def _preview(self):
        items = self.tree.selectedItems()
        if not items:
            return
        iss = items[0].data(0, _USER_ROLE)
        if iss is None:
            return
        lines = [iss.summary, ""]
        from modules.utility import chronology_check as CC
        if not iss.edits:
            # Le fasi si correggono nella scheda Periodizzazione, non in una
            # scheda US: la frase dipende da dove vive il dato.
            chiave = ("m_manual_fix_phases"
                      if CC.names_phases(getattr(iss, "kind", ""))
                      else "m_manual_fix_us")
            lines.append(RC._t(self._lang, chiave))
        for e in iss.edits:
            chi = CC.edit_prefix(e)
            for r in e.remove:
                lines.append(f"{chi}: rimuovi  {list(r)}")
            for a in e.add:
                lines.append(f"{chi}: aggiungi {list(a)}")
            for (col, val) in getattr(e, "set_fields", ()):
                lines.append(f"{chi}: imposta {col} = {val}")
        # La data calcolata delle US nominate: da dove viene, non solo quanto
        # vale. Si ricalcola a ogni verifica e non si scrive da nessuna parte.
        #
        # Solo per le categorie che nominano davvero delle US: l'`us_path` di
        # una sovrapposizione porta etichette di fase, e una fase senza nome
        # si legge col solo periodo — «4», che su un sito con la US 4 faceva
        # comparire la cronologia di quella US sotto un avviso che parlava
        # d'altro.
        righe_data = []
        nomina_fasi = CC.names_phases(getattr(iss, "kind", ""))
        # `rows` sta accanto a `us_path`, elemento per elemento: si cerca
        # prima la riga, perché su uno scavo a più aree il solo numero non
        # nomina una cronologia sola — e `bounds_by_us` quel numero non lo
        # indicizza nemmeno, per non mostrarne una a caso.
        righe_iss = list(getattr(iss, "rows", None) or ())
        elenco = (() if nomina_fasi
                  else getattr(iss, "us_path", ()) or ())
        for i, us in enumerate(elenco):
            riga = righe_iss[i] if i < len(righe_iss) else None
            chiave = RC._key_of_row(riga) if riga else None
            voce = ((self._chrono_bounds or {}).get(chiave)
                    or (self._chrono_bounds or {}).get(str(us)))
            testo = CC.explain_bounds(voce, lang=self._lang) if voce else ""
            if testo:
                righe_data.append("US %s · %s" % (us, testo))
        if righe_data:
            lines.extend([""] + righe_data)
        self.preview.setPlainText("\n".join(lines))

    def _apply(self):
        issues = self._selected_issues()
        edits = [e for iss in issues for e in iss.edits]
        if not edits:
            QMessageBox.information(self, "pyArchInit",
                                   "Nessuna correzione selezionata.")
            return
        sito = self.cboSite.currentText().strip()
        # Il sito dell'albero, non quello del selettore: fra «Esegui verifica»
        # e «Applica» il selettore si può muovere, e le spunte rimaste sono
        # quelle del sito di prima — applicarle qui scriverebbe le correzioni
        # di un sito sulle righe di un altro. Si rifiuta invece di svuotare
        # l'albero: le spunte sono lavoro dell'archeologo, e tornare sul sito
        # giusto le ritrova.
        atteso = getattr(self._report, "sito", None)
        if atteso and sito and sito != atteso:
            QMessageBox.warning(self, "pyArchInit",
                                RC._t(self._lang, "m_site_changed").format(
                                    atteso=atteso, scelto=sito))
            return
        if QMessageBox.question(
                self, "Conferma",
                f"Applicare {len(edits)} correzioni al sito '{sito}'?\n"
                f"(potrai annullare con 'Annulla ultimo fix')",
                QMessageBox.Yes | QMessageBox.No) != QMessageBox.Yes:
            return
        if any(getattr(e, "set_fields", ()) for e in edits):
            try:
                from pathlib import Path
                from scripts.migrations._common import (
                    auto_backup_sqlite, auto_backup_postgres, BackupSkipped)
                h = self._handle()
                if h.is_postgres:
                    _backup_dir = (
                        Path(pyarchinit_home()) / "pyarchinit_DB_folder"
                        / "_pga_backups"
                    )
                    _backup_dir.mkdir(parents=True, exist_ok=True)
                    auto_backup_postgres(h.engine, "temporal_fix", _backup_dir)
                elif h.sqlite_path:
                    auto_backup_sqlite(Path(h.sqlite_path), "temporal_fix")
            except BackupSkipped:
                if QMessageBox.question(
                        self, "Backup non disponibile",
                        "pg_dump non trovato: procedo senza backup?",
                        QMessageBox.Yes | QMessageBox.No) != QMessageBox.Yes:
                    return
            except Exception:
                pass   # backup is best-effort; rollback still protects
        try:
            self._token = RC.apply_edits(edits, self._handle(), sito=sito)
        except Exception as exc:
            QMessageBox.critical(self, "pyArchInit", f"Apply fallito: {exc}")
            return
        QMessageBox.information(self, "pyArchInit",
                               f"{len(edits)} correzioni applicate.")
        # La riverifica passa da `_render`, che azzera il token perché una
        # verifica lanciata a mano riparte da zero. Qui il token va tenuto: è
        # quello dell'applicazione appena fatta, e la conferma ha promesso
        # «potrai annullare con 'Annulla ultimo fix'».
        token = self._token
        self._run()  # re-scan to show the cleaned-up state
        self._token = token
        self.btnRollback.setEnabled(self._token is not None)

    def _run_genera_continuita(self):
        sito = self.cboSite.currentText().strip()
        if not sito:
            return
        from qgis.PyQt.QtWidgets import QDialogButtonBox
        from modules.s3dgraphy.sync import continuity_generator as CG
        try:
            handle = self._handle()
            schedatore = self._current_user()
            anche_le_fasi = self.chkPhases.isChecked()
            plan = CG.build_plan(handle, sito, schedatore=schedatore,
                                 lang=self._lang,
                                 include_phase=anche_le_fasi)
        except Exception as exc:
            QMessageBox.critical(self, "pyArchInit",
                                 f"Genera continuità fallita: {exc}")
            return
        if not (plan.to_create or plan.to_update or plan.orphan):
            # Perché non c'è niente, non solo che non c'è niente: la
            # regola guarda il periodo, e chi ha davanti una USM da 2/3 a
            # 2/4 deve sapere che gli manca una spunta, non un dato.
            coda = (f"({len(plan.unchanged)} già allineate)"
                    if plan.unchanged else
                    "Nessuna US/USM ha il periodo iniziale diverso dal "
                    "finale." + ("" if anche_le_fasi else
                                 "\nSe le tue unità cambiano solo fase "
                                 "dentro lo stesso periodo, spunta "
                                 "«anche i salti di fase»."))
            QMessageBox.information(
                self, "pyArchInit",
                f"Nessuna continuità da generare per '{sito}'.\n{coda}")
            return
        # Preview dialog
        dlg = QDialog(self)
        dlg.setWindowTitle("Anteprima continuità")
        lay = QVBoxLayout(dlg)
        summary = QTextEdit(); summary.setReadOnly(True)
        lines = [f"Sito: {sito}",
                 f"Da creare: {len(plan.to_create)}",
                 f"Da aggiornare: {len(plan.to_update)}",
                 f"Invariate: {len(plan.unchanged)}",
                 f"Orfane: {len(plan.orphan)}", ""]
        for d in plan.to_create:
            lines.append(f"  + {d['us']}  (periodi {d['periodo_iniziale']}→"
                         f"{d['periodo_finale']})")
        for d in plan.to_update:
            lines.append(f"  ~ {d['us']}  (periodi {d['periodo_iniziale']}→"
                         f"{d['periodo_finale']})")
        for us in plan.orphan:
            lines.append(f"  ? {us}  (orfana)")
        summary.setPlainText("\n".join(lines))
        lay.addWidget(summary)
        chkOrphans = QCheckBox("Rimuovi anche le CON orfane")
        chkOrphans.setEnabled(bool(plan.orphan))
        lay.addWidget(chkOrphans)
        bb = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        bb.button(QDialogButtonBox.Ok).setText("Genera")
        bb.accepted.connect(dlg.accept); bb.rejected.connect(dlg.reject)
        lay.addWidget(bb)
        dlg.resize(520, 460)
        if dlg.exec_() != QDialog.Accepted:
            return
        try:
            rep = CG.generate_continuity(
                handle, sito, schedatore=schedatore, lang=self._lang,
                remove_orphans=chkOrphans.isChecked(), do_backup=True,
                include_phase=anche_le_fasi)
        except Exception as exc:
            QMessageBox.critical(self, "pyArchInit",
                                 f"Generazione fallita: {exc}")
            return
        msg = (f"Continuità generata per '{sito}'.\n"
               f"Create: {rep.created} · Aggiornate: {rep.updated} · "
               f"Invariate: {rep.unchanged} · "
               f"Orfane rimosse: {rep.orphans_removed}")
        if rep.warnings:
            msg += "\n\nAvvisi:\n" + "\n".join(f"• {w}" for w in rep.warnings)
        QMessageBox.information(self, "pyArchInit", msg)

    def _current_user(self):
        try:
            from qgis.core import QgsSettings
            return (QgsSettings().value("pyarchinit/operatore", "", type=str)
                    or "")
        except Exception:
            return ""

    def _rollback(self):
        if self._token is None:
            # Non si torna in silenzio: un bottone che non risponde non si
            # distingue da un bottone rotto.
            QMessageBox.information(self, "pyArchInit",
                                    RC._t(self._lang, "m_nothing_to_undo"))
            self.btnRollback.setEnabled(False)
            return
        try:
            RC.rollback(self._token, self._handle())
        except Exception as exc:
            QMessageBox.critical(self, "pyArchInit", f"Rollback fallito: {exc}")
            return
        self._token = None
        self.btnRollback.setEnabled(False)
        QMessageBox.information(self, "pyArchInit", "Ultimo fix annullato.")
        self._run()


class RapportiCheckDialog(QDialog):
    """Standalone wrapper around :class:`RapportiCheckPanel`."""

    def __init__(self, iface=None, parent=None, db_provider=None):
        super().__init__(parent)
        self.iface = iface
        self.setWindowTitle("Verifica rapporti stratigrafici")
        lay = QVBoxLayout(self)
        self.panel = RapportiCheckPanel(iface=iface, db_provider=db_provider)
        lay.addWidget(self.panel)
        self.resize(760, 680)
