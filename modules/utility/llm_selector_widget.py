"""
Reusable Qt widget to pick an LLM provider + model.

Usage:

    selector = LLMSelectorWidget(scope="report")
    selector.config_changed.connect(my_handler)
    layout.addWidget(selector)
    cfg = selector.get_config()  # -> LLMConfig

The ``scope`` is used to persist a separate selection per AI feature
(e.g. report generator vs. text-to-SQL vs. RAG can each remember their
own preferred provider/model).

Pass ``vision_only=True`` to filter the model list to image-capable models,
which is what the ``skatch_gpt_*`` modules need.
"""

from qgis.PyQt.QtCore import QThread, Qt, pyqtSignal, pyqtSlot
from qgis.PyQt.QtWidgets import (
    QComboBox,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from .llm_providers import (
    PROVIDER_DEFAULTS,
    LLMConfig,
    LLMProvider,
    LLMProviderManager,
)


class _ModelDiscoveryThread(QThread):
    finished_signal = pyqtSignal(list, str)  # models, error_msg

    def __init__(self, provider: LLMProvider):
        super().__init__()
        self.provider = provider

    def run(self):
        try:
            if not LLMProviderManager.is_provider_available(self.provider):
                base = PROVIDER_DEFAULTS[self.provider]["base_url"]
                self.finished_signal.emit([], f"Server non raggiungibile su {base}")
                return
            models = LLMProviderManager.discover_models(self.provider)
            self.finished_signal.emit(models, "")
        except Exception as e:  # pragma: no cover - defensive
            self.finished_signal.emit([], str(e))


class LLMSelectorWidget(QWidget):
    """Reusable provider/model picker.

    Signals:
        config_changed(LLMConfig): emitted whenever provider, model or key
            changes. Connect to this if you want to react in real time.
    """

    config_changed = pyqtSignal(object)

    PROVIDER_LABELS = {
        LLMProvider.OPENAI: "OpenAI (Cloud)",
        LLMProvider.ANTHROPIC: "Anthropic Claude (Cloud)",
        LLMProvider.OLLAMA: "Ollama (Locale)",
        LLMProvider.LMSTUDIO: "LM Studio (Locale)",
    }

    def __init__(self, parent=None, scope: str = "default", vision_only: bool = False,
                 title: str = "Provider AI"):
        super().__init__(parent)
        self.scope = scope
        self.vision_only = vision_only
        self._discovery_thread = None
        self._loading = False
        self._setup_ui(title)
        self._load_saved_config()

    # ----------------------------------------------------------------- ui

    def _setup_ui(self, title: str):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        group = QGroupBox(title)
        layout = QVBoxLayout(group)

        # Provider row
        row1 = QHBoxLayout()
        row1.addWidget(QLabel("Provider:"))
        self.provider_combo = QComboBox()
        for p in LLMProvider:
            self.provider_combo.addItem(self.PROVIDER_LABELS[p], p)
        self.provider_combo.currentIndexChanged.connect(self._on_provider_changed)
        row1.addWidget(self.provider_combo, 1)

        self.refresh_btn = QPushButton("Aggiorna modelli")
        self.refresh_btn.setToolTip(
            "Per Ollama / LM Studio interroga il server locale e mostra i modelli installati."
        )
        self.refresh_btn.clicked.connect(lambda: self._refresh_models())
        row1.addWidget(self.refresh_btn)
        layout.addLayout(row1)

        # Model row
        row2 = QHBoxLayout()
        row2.addWidget(QLabel("Modello:"))
        self.model_combo = QComboBox()
        self.model_combo.setEditable(True)
        self.model_combo.setMinimumWidth(280)
        self.model_combo.currentIndexChanged.connect(self._on_model_changed)
        self.model_combo.editTextChanged.connect(self._on_model_changed)
        row2.addWidget(self.model_combo, 1)
        layout.addLayout(row2)

        # API key row
        row3 = QHBoxLayout()
        self.api_key_label = QLabel("API key:")
        row3.addWidget(self.api_key_label)
        self.api_key_edit = QLineEdit()
        self.api_key_edit.setEchoMode(QLineEdit.Password)
        self.api_key_edit.editingFinished.connect(self._save_api_key)
        row3.addWidget(self.api_key_edit, 1)
        self.show_key_btn = QPushButton("Mostra")
        self.show_key_btn.setCheckable(True)
        self.show_key_btn.setMaximumWidth(70)
        self.show_key_btn.toggled.connect(
            lambda v: self.api_key_edit.setEchoMode(
                QLineEdit.Normal if v else QLineEdit.Password
            )
        )
        row3.addWidget(self.show_key_btn)
        layout.addLayout(row3)

        # Status / test
        row4 = QHBoxLayout()
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: gray; font-style: italic;")
        row4.addWidget(self.status_label, 1)
        self.test_btn = QPushButton("Test connessione")
        self.test_btn.clicked.connect(self._test_connection)
        row4.addWidget(self.test_btn)
        layout.addLayout(row4)

        outer.addWidget(group)

    # ------------------------------------------------------------- helpers

    def _set_provider(self, provider: LLMProvider):
        idx = self.provider_combo.findData(provider)
        if idx >= 0:
            self._loading = True
            self.provider_combo.setCurrentIndex(idx)
            self._loading = False

    def _is_local(self) -> bool:
        provider = self.provider_combo.currentData()
        return provider is not None and PROVIDER_DEFAULTS[provider]["is_local"]

    def _load_saved_config(self):
        cfg = LLMProviderManager.load_config(self.scope)
        if cfg is None:
            cfg = LLMConfig(provider=LLMProvider.OPENAI)
        self._loading = True
        try:
            self._set_provider(cfg.provider)
            # api key visibility / value
            self._update_api_key_visibility(cfg.provider)
            if cfg.needs_api_key:
                self.api_key_edit.setText(LLMProviderManager.get_api_key(cfg.provider))
            else:
                self.api_key_edit.clear()
        finally:
            self._loading = False
        self._refresh_models(saved_model=cfg.model)

    def _update_api_key_visibility(self, provider: LLMProvider):
        is_local = PROVIDER_DEFAULTS[provider]["is_local"]
        self.api_key_label.setVisible(not is_local)
        self.api_key_edit.setVisible(not is_local)
        self.show_key_btn.setVisible(not is_local)

    # --------------------------------------------------------------- slots

    def _on_provider_changed(self, _idx):
        if self._loading:
            return
        provider = self.provider_combo.currentData()
        if provider is None:
            return
        self._update_api_key_visibility(provider)
        if PROVIDER_DEFAULTS[provider]["needs_api_key"]:
            self.api_key_edit.setText(LLMProviderManager.get_api_key(provider))
        else:
            self.api_key_edit.clear()
        self._refresh_models()
        self._save_config()
        self._emit_config()

    def _refresh_models(self, saved_model: str = ""):
        provider = self.provider_combo.currentData()
        if provider is None:
            return
        self._loading = True
        self.model_combo.clear()
        self._loading = False
        defaults = PROVIDER_DEFAULTS[provider]

        if not defaults["is_local"]:
            models = list(defaults["default_models"])
            if self.vision_only:
                models = LLMProviderManager.filter_vision_models(provider, models)
            self._populate_models(models, saved_model)
            self.status_label.setText("")
            return

        # Local: discover async
        self.status_label.setText("Ricerca modelli installati...")
        if self._discovery_thread and self._discovery_thread.isRunning():
            self._discovery_thread.quit()
            self._discovery_thread.wait(100)
        self._discovery_thread = _ModelDiscoveryThread(provider)
        self._discovery_thread.finished_signal.connect(
            lambda models, err: self._on_models_discovered(models, err, saved_model)
        )
        self._discovery_thread.start()

    @pyqtSlot(list, str)
    def _on_models_discovered(self, models, err, saved_model: str = ""):
        provider = self.provider_combo.currentData()
        if self.vision_only and provider is not None:
            models = LLMProviderManager.filter_vision_models(provider, models)
        if err:
            self.status_label.setText(err)
        elif not models:
            self.status_label.setText(self._empty_models_message(provider))
        else:
            self.status_label.setText(f"{len(models)} modelli caricati e pronti")
        self._populate_models(models, saved_model)

    def _empty_models_message(self, provider) -> str:
        """Build a provider-specific message when no usable model was found.

        For LM Studio we distinguish between "server down" and "server up but
        no model loaded into RAM" — the latter is the most common gotcha:
        chat calls fail with 400 ``No models loaded``. We probe the native
        endpoint to know which case we're in.
        """
        if provider == LLMProvider.LMSTUDIO:
            all_models = LLMProviderManager.discover_all_models(provider)
            if all_models:
                # Server is up, models exist but none loaded
                names = ", ".join(m["id"] for m in all_models[:3])
                more = "..." if len(all_models) > 3 else ""
                return (
                    f"Nessun modello caricato in LM Studio. "
                    f"Carica un modello con 'lms load <nome>' o dalla scheda "
                    f"Developer di LM Studio.\nDisponibili (scaricati): {names}{more}"
                )
            return (
                "LM Studio non risponde. Verifica che sia in esecuzione su "
                f"{PROVIDER_DEFAULTS[provider]['base_url']}."
            )
        if provider == LLMProvider.OLLAMA:
            return (
                "Nessun modello installato in Ollama. Installa con "
                "'ollama pull <nome>' (es. 'ollama pull llama3.2')."
            )
        base = PROVIDER_DEFAULTS[provider]["base_url"] if provider else "il server"
        return f"Nessun modello trovato su {base}."

    def _populate_models(self, models, saved_model: str = ""):
        self._loading = True
        try:
            self.model_combo.clear()
            for m in models:
                self.model_combo.addItem(m)
            if saved_model:
                idx = self.model_combo.findText(saved_model)
                if idx >= 0:
                    self.model_combo.setCurrentIndex(idx)
                elif models:
                    # Saved model is not currently loaded/available — pick the
                    # first usable one and mention what happened in the status.
                    # Otherwise we'd silently send chat requests to a model
                    # that isn't loaded and get a 400 from the server.
                    self.model_combo.setCurrentIndex(0)
                    cur = self.status_label.text()
                    note = f" (modello salvato '{saved_model}' non caricato → uso {models[0]})"
                    if note not in cur:
                        self.status_label.setText(cur + note)
                else:
                    # No models at all — keep the saved name visible so the
                    # user can see what was previously chosen.
                    self.model_combo.setEditText(saved_model)
        finally:
            self._loading = False
        # Persist the actual current selection (auto-picked or user-saved)
        provider = self.provider_combo.currentData()
        if provider is not None and self.model_combo.currentText():
            LLMProviderManager.save_config(self.get_config(), self.scope)
        self._emit_config()

    def _on_model_changed(self, *_):
        if self._loading:
            return
        self._save_config()
        self._emit_config()

    def _save_api_key(self):
        provider = self.provider_combo.currentData()
        if provider is None or PROVIDER_DEFAULTS[provider]["is_local"]:
            return
        key = self.api_key_edit.text().strip()
        if key:
            LLMProviderManager.save_api_key(provider, key)
        self._emit_config()

    def _save_config(self):
        if self._loading:
            return
        LLMProviderManager.save_config(self.get_config(), self.scope)

    def _emit_config(self):
        if self._loading:
            return
        self.config_changed.emit(self.get_config())

    def _test_connection(self):
        cfg = self.get_config()
        if not cfg.model:
            QMessageBox.warning(self, "Test connessione", "Seleziona prima un modello.")
            return
        if cfg.needs_api_key and not cfg.api_key:
            QMessageBox.warning(
                self, "Test connessione", "API key mancante per questo provider."
            )
            return
        try:
            text = LLMProviderManager.chat(
                cfg,
                [{"role": "user", "content": "Ciao, rispondi solo con OK."}],
                max_tokens=20,
            )
            if text:
                QMessageBox.information(
                    self,
                    "Test connessione",
                    f"OK — risposta da {cfg.provider.value} ({cfg.model}):\n\n{text[:200]}",
                )
            else:
                QMessageBox.warning(
                    self,
                    "Test connessione",
                    f"Risposta vuota da {cfg.provider.value}/{cfg.model}.",
                )
        except Exception as e:
            QMessageBox.critical(self, "Test connessione", f"Errore: {e}")

    # ---------------------------------------------------------------- api

    def get_config(self) -> LLMConfig:
        provider = self.provider_combo.currentData() or LLMProvider.OPENAI
        model = self.model_combo.currentText().strip()
        api_key = ""
        if PROVIDER_DEFAULTS[provider]["needs_api_key"]:
            api_key = self.api_key_edit.text().strip() or LLMProviderManager.get_api_key(
                provider
            )
        return LLMConfig(provider=provider, model=model, api_key=api_key)

    def set_provider(self, provider: LLMProvider):
        """Programmatically switch provider (also persists)."""
        self._set_provider(provider)
        self._on_provider_changed(self.provider_combo.currentIndex())
