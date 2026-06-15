# -*- coding: utf-8 -*-
"""
AI descriptive report for the palimpsestr SEF analysis.

After the R side (palimpsestr) has produced the Stratigraphic Entanglement
Field results — the interpretive markdown narrative, the diagnostic tables and
the ``gg_*`` figures — this module runs a small pipeline of **specialised LLM
agents** over those facts and produces a single, didactic, human-readable
report **in any pyArchInit UI language**:

    1. Methodologist — explains *why* the analysis was parameterised the way it
       was: the class model (multinomial vs gaussian), the number of phases K
       (and what the diagnostics say about that choice), the noise/outlier
       component and intrusion threshold, and the finds source. States caveats.
    2. Analyst — interprets the results: phase composition and chronology
       (using the absolute OxCal dates from ``palimpsest_chronology`` when
       present), residuality / intrusions, spatial pattern.
    3. Synthesiser — weaves the two into one cohesive report, references the
       figures, and closes with conclusions and recommendations.

The agents are driven through ``LLMProviderManager.stream_chat`` (OpenAI /
Anthropic / Ollama / LM Studio), which is Qt-free and therefore safe to call
from the worker thread. Provider/model are chosen with the shared
``LLMSelectorWidget``. The result is shown live and can be saved as DOCX (with
the figures embedded) or Markdown.

@author: Enzo Cocca <enzo.ccc@gmail.com>
"""
import os

from qgis.PyQt.QtCore import QThread, pyqtSignal
from qgis.PyQt.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel, QComboBox,
    QCheckBox, QPushButton, QPlainTextEdit, QMessageBox, QFileDialog)

from modules.utility.llm_providers import LLMProviderManager
from modules.utility.llm_selector_widget import LLMSelectorWidget


# pyArchInit UI languages (code -> name shown in the combo + given to the LLM).
AI_LANGUAGES = [
    ("it", "Italiano"), ("en", "English"), ("de", "Deutsch"),
    ("es", "Español"), ("fr", "Français"), ("pt", "Português"),
    ("ca", "Català"), ("ro", "Română"), ("el", "Ελληνικά"),
    ("ar", "العربية"),
]

# What each gg_* figure shows — handed to the synthesiser so it can reference
# them meaningfully and used as DOCX captions.
FIGURE_CAPTIONS = {
    "phasefield": "Campo di fase / phase field (SEF)",
    "entropy": "Entropia di assegnazione per US / assignment entropy per US",
    "energy": "Energia del campo / field energy",
    "intrusions": "Intrusioni e residualità / intrusions and residuality",
    "phase_composition": "Composizione dei reperti per fase / finds composition by phase",
    "direction": "Direzione cronologica / chronological direction",
    "outliers": "Outlier posteriori / posterior outliers",
    "unit_coherence": "Coerenza delle US / unit coherence",
}


def _model_name(idx):
    return ("multinomial", "gaussian")[idx] if idx in (0, 1) else str(idx)


def _source_name(idx):
    return ("entrambi (materiali+ceramica)", "solo materiali", "solo ceramica")[idx] \
        if idx in (0, 1, 2) else str(idx)


def _facts_block(facts):
    """Compact, model-agnostic description of the run, fed to every agent."""
    lines = [
        "PARAMETRI DELL'ANALISI SEF (palimpsestr):",
        "- Sito: %s" % facts.get("site", "tutti"),
        "- Backend dati: %s" % facts.get("backend", "?"),
        "- Numero di fasi richieste K = %s" % facts.get("k"),
        "- Modello di classe = %s" % facts.get("class_model"),
        "- Componente di rumore/outlier = %s" % ("attiva" if facts.get("noise") else "disattiva"),
        "- Soglia intrusioni = %s" % facts.get("threshold"),
        "- Selezione reperti = %s" % facts.get("source"),
        "- Cronologia assoluta (tabella palimpsest_chronology) = %s"
        % ("presente, usata al posto della datazione testuale"
           if facts.get("has_chronology") else "assente (si usa la datazione testuale)"),
        "",
        "NARRATIVA E TABELLE DIAGNOSTICHE PRODOTTE DA palimpsestr (fonte di verità, NON inventare numeri):",
        facts.get("r_markdown", "(nessuna narrativa R disponibile)"),
    ]
    if facts.get("figures"):
        lines += ["", "FIGURE DISPONIBILI (riferiscile per nome quando utile):"]
        for key in facts["figures"]:
            lines.append("- %s: %s" % (key, FIGURE_CAPTIONS.get(key, key)))
    return "\n".join(lines)


def _methodologist_prompt(facts, lang_name):
    return (
        "Sei un metodologo dell'archeologia quantitativa, esperto del modello "
        "Stratigraphic Entanglement Field (SEF) di palimpsestr per la "
        "decomposizione probabilistica dei palinsesti.\n\n"
        + _facts_block(facts) +
        "\n\nCompito: spiega in modo chiaro e didattico le SCELTE METODOLOGICHE "
        "di questa analisi, giustificandole con le diagnostiche fornite:\n"
        "1. Perché il modello di classe scelto (multinomiale vs gaussiano) è "
        "adatto a questi dati, e cosa cambierebbe con l'altro.\n"
        "2. Il numero di fasi K: se K è appropriato alla luce di entropia, "
        "coerenza delle US ed energia del campo; segnala se i dati "
        "suggerirebbero un K diverso.\n"
        "3. La componente di rumore/outlier e la soglia di intrusione: cosa "
        "implicano e come leggere i risultati di residualità.\n"
        "4. La selezione dei reperti (materiali/ceramica/entrambi) e l'uso "
        "della cronologia assoluta OxCal se presente.\n"
        "Indica i limiti e le cautele interpretative. Non inventare numeri: "
        "usa solo quelli nelle diagnostiche. "
        "Scrivi ESCLUSIVAMENTE in %s, in prosa tecnica ma comprensibile." % lang_name
    )


def _analyst_prompt(facts, lang_name):
    return (
        "Sei un archeologo stratigrafo esperto di formazione dei depositi e "
        "di analisi dei palinsesti.\n\n"
        + _facts_block(facts) +
        "\n\nCompito: INTERPRETA i risultati dell'analisi SEF:\n"
        "1. Composizione e significato delle fasi individuate (cosa "
        "rappresentano in termini di reperti e di cronologia).\n"
        "2. Cronologia: se è presente la cronologia assoluta (OxCal), discuti "
        "gli intervalli calendariali per fase e la direzione cronologica.\n"
        "3. Residualità e intrusioni: quali US/reperti risultano fuori posto e "
        "cosa dice questo sui processi di formazione del deposito.\n"
        "4. Eventuale pattern spaziale.\n"
        "Fonda ogni affermazione sulle diagnostiche fornite. "
        "Scrivi ESCLUSIVAMENTE in %s." % lang_name
    )


def _synthesis_prompt(facts, lang_name, methodology, analysis):
    return (
        "Sei il redattore scientifico che redige il report finale dell'analisi "
        "SEF (palimpsestr) per una relazione archeologica.\n\n"
        "Hai a disposizione:\n\n=== NOTA METODOLOGICA ===\n" + methodology +
        "\n\n=== INTERPRETAZIONE ===\n" + analysis +
        "\n\n" + _facts_block(facts) +
        "\n\nCompito: scrivi un UNICO report coeso, ben strutturato e "
        "comprensibile, con titoli di sezione, che integri nota metodologica e "
        "interpretazione. DEVE includere, in modo esplicito e argomentato: la "
        "scelta del modello (multinomiale o gaussiano) e il perché; il valore "
        "di K e perché; il significato della soglia/rumore; la selezione dei "
        "reperti; e i risultati con la loro lettura archeologica. Richiama le "
        "figure pertinenti per nome quando illustrano un punto. Chiudi con "
        "conclusioni e raccomandazioni operative. Non inventare numeri. "
        "Scrivi ESCLUSIVAMENTE in %s. Usa Markdown (titoli con #, elenchi)." % lang_name
    )


class PalimpsestAIReportWorker(QThread):
    """Runs the 3-agent pipeline off the UI thread."""

    chunk = pyqtSignal(str)       # streamed text
    status = pyqtSignal(str)      # phase label
    finished_ok = pyqtSignal(str)  # full assembled markdown
    failed = pyqtSignal(str)

    def __init__(self, facts, config, lang_code, lang_name):
        super().__init__()
        self.facts = facts
        self.config = config
        self.lang_code = lang_code
        self.lang_name = lang_name

    def _run_agent(self, prompt, emit_live):
        out = []
        for ch in LLMProviderManager.stream_chat(
                self.config, messages=[{"role": "user", "content": prompt}],
                max_tokens=4096):
            out.append(ch)
            if emit_live:
                self.chunk.emit(ch)
        return "".join(out)

    def run(self):
        try:
            self.status.emit("methodology")
            method = self._run_agent(
                _methodologist_prompt(self.facts, self.lang_name), emit_live=False)
            self.status.emit("analysis")
            analysis = self._run_agent(
                _analyst_prompt(self.facts, self.lang_name), emit_live=False)
            self.status.emit("synthesis")
            final = self._run_agent(
                _synthesis_prompt(self.facts, self.lang_name, method, analysis),
                emit_live=True)
            self.finished_ok.emit(final.strip())
        except Exception as e:  # noqa: BLE001 — surfaced to the UI thread
            self.failed.emit(str(e))


class PalimpsestAIReportDialog(QDialog):
    """Provider/language picker + live panel + DOCX/MD save for the AI report."""

    def __init__(self, parent_dlg, facts):
        super().__init__(parent_dlg)
        self.p = parent_dlg
        self.facts = facts
        self.worker = None
        self._final_md = ""
        self.setWindowTitle("palimpsestr — Report AI (analisi descrittiva)")
        self.resize(760, 560)
        self._build_ui()

    def _build_ui(self):
        lay = QVBoxLayout(self)
        lay.addWidget(QLabel(
            "Genera una relazione descrittiva dell'analisi SEF con agenti AI "
            "specializzati (metodologo, analista, redattore). Spiega le scelte "
            "di modello, K, soglia e reperti, interpreta i risultati e include "
            "le figure."))

        form = QFormLayout()
        self.llm = LLMSelectorWidget(scope="palimpsest_report", title="")
        form.addRow("Provider AI:", self.llm)
        self.combo_lang = QComboBox()
        for code, name in AI_LANGUAGES:
            self.combo_lang.addItem(name, code)
        form.addRow("Lingua del report:", self.combo_lang)
        lay.addLayout(form)

        opts = QHBoxLayout()
        self.chk_figs = QCheckBox("Includi figure nel DOCX")
        self.chk_figs.setChecked(bool(self.facts.get("figures")))
        self.chk_figs.setEnabled(bool(self.facts.get("figures")))
        opts.addWidget(self.chk_figs)
        opts.addStretch()
        lay.addLayout(opts)

        self.panel = QPlainTextEdit()
        self.panel.setReadOnly(True)
        self.panel.setPlaceholderText(
            "Il report apparirà qui durante la generazione.")
        lay.addWidget(self.panel)

        self.status = QLabel("")
        lay.addWidget(self.status)

        row = QHBoxLayout()
        self.btn_run = QPushButton("Genera report AI")
        self.btn_run.clicked.connect(self._run)
        self.btn_save_docx = QPushButton("Salva DOCX…")
        self.btn_save_docx.clicked.connect(self._save_docx)
        self.btn_save_docx.setEnabled(False)
        self.btn_save_md = QPushButton("Salva Markdown…")
        self.btn_save_md.clicked.connect(self._save_md)
        self.btn_save_md.setEnabled(False)
        btn_close = QPushButton("Chiudi")
        btn_close.clicked.connect(self.accept)
        row.addWidget(self.btn_run); row.addWidget(self.btn_save_docx)
        row.addWidget(self.btn_save_md); row.addWidget(btn_close)
        lay.addLayout(row)

    # ------------------------------------------------------------- run/stream ---
    _STATUS = {
        "methodology": "Agente metodologo: spiego le scelte (modello, K, soglia)…",
        "analysis": "Agente analista: interpreto fasi, cronologia, intrusioni…",
        "synthesis": "Agente redattore: compongo il report finale…",
    }

    def _run(self):
        config = self.llm.get_config()
        if not config.model:
            QMessageBox.warning(self, "palimpsestr",
                                "Seleziona un modello AI nel selettore Provider.")
            return
        if config.needs_api_key and not config.api_key:
            QMessageBox.warning(self, "palimpsestr",
                                "Manca l'API key per il provider scelto.")
            return
        self.panel.setPlainText("")
        self._final_md = ""
        self.btn_run.setEnabled(False)
        self.btn_save_docx.setEnabled(False)
        self.btn_save_md.setEnabled(False)
        code = self.combo_lang.currentData()
        name = self.combo_lang.currentText()
        self.worker = PalimpsestAIReportWorker(self.facts, config, code, name)
        self.worker.status.connect(self._on_status)
        self.worker.chunk.connect(self._on_chunk)
        self.worker.finished_ok.connect(self._on_done)
        self.worker.failed.connect(self._on_failed)
        self.worker.start()

    def _on_status(self, phase):
        self.status.setText(self._STATUS.get(phase, phase))

    def _on_chunk(self, text):
        self.panel.insertPlainText(text)
        sb = self.panel.verticalScrollBar()
        sb.setValue(sb.maximum())

    def _on_done(self, md):
        self._final_md = md
        if md and not self.panel.toPlainText().strip():
            self.panel.setPlainText(md)
        self.status.setText("Report completato.")
        self.btn_run.setEnabled(True)
        self.btn_save_docx.setEnabled(True)
        self.btn_save_md.setEnabled(True)

    def _on_failed(self, err):
        self.status.setText("")
        self.btn_run.setEnabled(True)
        QMessageBox.critical(self, "palimpsestr",
                             "Generazione del report AI fallita:\n%s" % err)

    # ----------------------------------------------------------------- save ---
    def _save_md(self):
        if not self._final_md:
            return
        fn, _ = QFileDialog.getSaveFileName(
            self, "Salva report (Markdown)", self.p.HOME, "Markdown (*.md)")
        if not fn:
            return
        if not fn.lower().endswith(".md"):
            fn += ".md"
        try:
            with open(fn, "w", encoding="utf-8") as f:
                f.write(self._final_md)
        except Exception as e:
            QMessageBox.critical(self, "palimpsestr", "Salvataggio fallito:\n%s" % e)
            return
        self.status.setText("Salvato: %s" % fn)

    def _save_docx(self):
        if not self._final_md:
            return
        fn, _ = QFileDialog.getSaveFileName(
            self, "Salva report (DOCX)", self.p.HOME, "Word (*.docx)")
        if not fn:
            return
        if not fn.lower().endswith(".docx"):
            fn += ".docx"
        try:
            self._write_docx(fn)
        except Exception as e:
            QMessageBox.critical(self, "palimpsestr", "Salvataggio DOCX fallito:\n%s" % e)
            return
        self.status.setText("Salvato: %s" % fn)
        QMessageBox.information(self, "palimpsestr", "Report salvato:\n%s" % fn)

    def _write_docx(self, path):
        """Render the markdown narrative to DOCX and append the figures."""
        from docx import Document
        from docx.shared import Pt, Inches
        doc = Document()
        for raw in self._final_md.splitlines():
            line = raw.rstrip()
            if not line.strip():
                continue
            if line.startswith("#"):
                level = len(line) - len(line.lstrip("#"))
                doc.add_heading(line.lstrip("# ").strip(), level=min(level, 4))
            elif line.lstrip().startswith(("- ", "* ")):
                p = doc.add_paragraph(line.lstrip()[2:], style="List Bullet")
                for r in p.runs:
                    r.font.name = "Cambria"; r.font.size = Pt(11)
            else:
                p = doc.add_paragraph(line)
                for r in p.runs:
                    r.font.name = "Cambria"; r.font.size = Pt(11)
        if self.chk_figs.isChecked() and self.facts.get("figures_dir"):
            doc.add_heading("Figure", level=1)
            fdir = self.facts["figures_dir"]
            for key in self.facts.get("figures", []):
                png = os.path.join(fdir, key + ".png")
                if os.path.exists(png):
                    try:
                        doc.add_picture(png, width=Inches(6.0))
                    except Exception:
                        continue
                    cap = doc.add_paragraph(FIGURE_CAPTIONS.get(key, key))
                    for r in cap.runs:
                        r.font.name = "Cambria"; r.font.size = Pt(9)
        doc.save(path)
