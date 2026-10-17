"""La scheda «Narrativa» del pannello della matrice (2026-10-12).

Qt sta qui; la logica sta in ``em_narrative`` (puro) e il lato grafo
nella libreria. La scheda legge e scrive **lo stesso em.json** che il
pannello disegna e che EMStudio apre: niente copie.

Spec: docs/superpowers/specs/2026-10-12-narrativa-ai-design.md
"""
from __future__ import annotations

import os
from typing import List, Optional

from urllib.parse import unquote

from qgis.PyQt.QtCore import QThread, pyqtSignal
from qgis.PyQt.QtWidgets import (QComboBox, QFileDialog, QHBoxLayout, QInputDialog, QLabel,
                                 QListWidget, QListWidgetItem, QMenu, QMessageBox,
                                 QPushButton, QTextBrowser, QVBoxLayout, QWidget)

from . import em_narrative as en


def _lang() -> str:
    try:
        from qgis.core import QgsSettings
        return (QgsSettings().value("locale/userLocale", "it", type=str) or "it")[:2]
    except Exception:                               # noqa: BLE001
        return "it"


_L = {
    "tab": {"it": "Narrativa", "en": "Narrative"},
    "tab_units": {"it": "Unità", "en": "Units"},
    "no_ai": {"it": "Nessuna AI impostata: impostala nella scheda US con «Report» "
                    "(Provider AI) o con «Query AI Database».",
              "en": "No AI configured: set it in the US form with “Report” "
                    "(AI provider) or with “Query AI Database”."},
    "empty": {"it": "Nessuna narrativa nel file: «Prepara i capitoli» crea lo scheletro "
                    "({n} capitoli fra epoche e attività), «Genera con l'AI» lo scrive.",
              "en": "No narrative in the file: “Prepare the chapters” builds the outline "
                    "({n} chapters over epochs and activities), “Generate with AI” writes it."},
    "generate": {"it": "Genera con l'AI", "en": "Generate with AI"},
    "regenerate": {"it": "Rigenera capitolo", "en": "Regenerate chapter"},
    "endorse": {"it": "Convalida…", "en": "Endorse…"},
    "endorse_chapter": {"it": "Questo capitolo", "en": "This chapter"},
    "endorse_all": {"it": "Tutti i capitoli", "en": "All chapters"},
    "prepare": {"it": "Prepara i capitoli", "en": "Prepare the chapters"},
    "export": {"it": "Esporta…", "en": "Export…"},
    "emstudio": {"it": "Apri in EMStudio", "en": "Open in EMStudio"},
    "map": {"it": "Mostra sulla mappa", "en": "Show on the map"},
    "cancel": {"it": "Annulla", "en": "Cancel"},
    "progress": {"it": "Capitolo {i} di {n} · {title}", "en": "Chapter {i} of {n} · {title}"},
    "starting": {"it": "Avvio…", "en": "Starting…"},
    "who": {"it": "Chi convalida? Scegli un autore o scrivi un nome nuovo.",
            "en": "Who endorses? Pick an author or type a new name."},
    "endorsed": {"it": "{n} blocchi convalidati da {who}.", "en": "{n} blocks endorsed by {who}."},
    "nothing_to_endorse": {"it": "Niente da convalidare.", "en": "Nothing to endorse."},
    "export_filter": {"it": "Pagina HTML (*.html);;Documento Word (*.docx);;PDF stampabile (*.pdf)",
                      "en": "HTML page (*.html);;Word document (*.docx);;Printable PDF (*.pdf)"},
    "exported": {"it": "Narrativa esportata in {path}", "en": "Narrative exported to {path}"},
    "emstudio_missing": {"it": "EMStudio non risulta installato: menu Extended Matrix → "
                               "Installa EMStudio…",
                         "en": "EMStudio is not installed: menu Extended Matrix → "
                               "«Installa EMStudio…»"},
    "prepared": {"it": "Capitoli preparati: {n}.", "en": "Chapters prepared: {n}."},
    "title": {"it": "Narrativa", "en": "Narrative"},
    "busy": {"it": "Generazione in corso: aspetta che finisca, o premi Annulla, prima di "
                   "cambiare file.",
             "en": "Generation in progress: wait for it to finish, or press Cancel, before "
                   "changing file."},
    "language": {"it": "Lingua della prosa:", "en": "Language of the prose:"},
    "language_tip": {"it": "La lingua in cui l'AI scrive i capitoli e in cui nascono i titoli dei "
                           "capitoli nuovi. Parte da quella della narrativa del file, se ne ha una, "
                           "altrimenti da quella di QGIS. I capitoli già scritti non si traducono.",
                     "en": "The language the AI writes the chapters in, and the one new chapter "
                           "titles are born in. It starts from the language of the file's narrative, "
                           "if it has one, otherwise from QGIS's. Chapters already written are not "
                           "translated."},
    "ask_title": {"it": "Prepara i capitoli", "en": "Prepare the chapters"},
    "ask_text": {"it": "La narrativa del file ha già i suoi {n} capitoli. Aggiungo anche quelli di "
                       "pyArchInit — la presentazione, il luogo, un capitolo per ogni epoca e per "
                       "ogni attività che non ne ha uno —, in coda ai suoi?",
                 "en": "The file's narrative already has its own {n} chapters. Shall I add "
                       "pyArchInit's too — the presentation, the place, one chapter for each epoch "
                       "and each activity that has none —, after its own?"},
    "only_file": {"it": "Solo i capitoli del file", "en": "Only the file's chapters"},
    "add_ours": {"it": "Aggiungi quelli di pyArchInit", "en": "Add pyArchInit's"},
    "kept_file": {"it": "Restano i {n} capitoli del file: nessun capitolo aggiunto.",
                  "en": "The file's {n} chapters stay as they are: no chapter added."},
    "close_emstudio": {"it": "Se EMStudio ha il file aperto, chiudilo prima: chi scrive "
                             "per ultimo vince.",
                       "en": "If EMStudio has the file open, close it first: the last "
                             "writer wins."},
}


def _t(key: str, **kw) -> str:
    voce = _L[key]
    return voce.get(_lang(), voce["en"]).format(**kw)


#: Le lingue in cui l'AI può scrivere: quelle di pyArchInit, col loro nome.
_LINGUE = (("it", "Italiano"), ("en", "English"), ("de", "Deutsch"), ("fr", "Français"),
           ("es", "Español"), ("ca", "Català"), ("pt", "Português"), ("ro", "Română"),
           ("el", "Ελληνικά"), ("ar", "العربية"))


def _chiedi_capitoli(parent, quanti: int) -> Optional[str]:
    """«Prepara i capitoli» su una narrativa che il file porta di suo: solo
    i suoi capitoli («file»), anche quelli di pyArchInit («pyarchinit»), o
    niente (None). Si chiede ogni volta (Enzo, 17 ottobre 2026)."""
    box = QMessageBox(parent)
    box.setIcon(QMessageBox.Icon.Question)
    box.setWindowTitle(_t("ask_title"))
    box.setText(_t("ask_text", n=quanti))
    solo = box.addButton(_t("only_file"), QMessageBox.ButtonRole.RejectRole)
    nostri = box.addButton(_t("add_ours"), QMessageBox.ButtonRole.AcceptRole)
    box.addButton(QMessageBox.StandardButton.Cancel)
    box.setDefaultButton(solo)
    fn = getattr(box, "exec", None) or getattr(box, "exec_")
    fn()
    premuto = box.clickedButton()
    if premuto is solo:
        return "file"
    if premuto is nostri:
        return "pyarchinit"
    return None


def _exec(menu, pos):
    """``exec`` in Qt6, ``exec_`` in Qt5."""
    fn = getattr(menu, "exec", None) or getattr(menu, "exec_")
    return fn(pos)


class NarrativeThread(QThread):
    """Genera fuori dal filo dell'interfaccia e salva alla fine."""

    progress = pyqtSignal(int, int, str)
    finished_ok = pyqtSignal(bool, str)

    def __init__(self, path, cfg, lang, anchors=None, parent=None, write_lang=None):
        super().__init__(parent)
        self._path, self._cfg, self._lang = str(path), cfg, lang
        self._write_lang = write_lang
        self._anchors = list(anchors) if anchors is not None else None
        self._stop = False

    def cancel(self):
        self._stop = True

    def _chat(self, messages):
        from ..utility.llm_providers import LLMProviderManager
        meta = {}
        testo = "".join(LLMProviderManager.stream_chat(
            self._cfg, messages, max_tokens=en.MAX_TOKENS, meta=meta))
        return testo, bool(meta.get("truncated"))

    def run(self):                                  # noqa: D401
        try:
            contenitore, _ = en.load_project(self._path)
            rapporto = en.generate(
                contenitore, chat=self._chat, model=str(getattr(self._cfg, "model", "")),
                lang=self._lang, anchors=self._anchors, write_lang=self._write_lang,
                progress=lambda i, n, t: self.progress.emit(i, n, t),
                cancelled=lambda: self._stop)
            if rapporto.outcomes:
                en.save_project(contenitore, self._path)
            self.finished_ok.emit(rapporto.failed == 0 and not rapporto.cancelled,
                                  rapporto.summary(self._lang))
        except Exception as e:                      # noqa: BLE001
            self.finished_ok.emit(False, str(e))


class _State:
    def __init__(self):
        self.path: Optional[str] = None
        self.views: List[en.ChapterView] = []
        self.thread: Optional[NarrativeThread] = None
        self.config = None
        self.iface = None
        self.conn = None
        self.media_cache: dict = {}
        #: il file per cui la lingua della prosa è già stata proposta
        self.lingua_di: Optional[str] = None


def _running(stato: "_State") -> bool:
    t = stato.thread
    try:
        return t is not None and bool(t.isRunning())
    except RuntimeError:                           # già distrutto da Qt
        return False


def _say(iface, livello: str, messaggio: str) -> None:
    try:
        barra = iface.messageBar()
        (barra.pushInfo if livello == "info" else barra.pushWarning)(_t("title"), messaggio)
    except Exception:                               # noqa: BLE001
        pass


def export_target(percorso: str, filtro: str):
    """``(percorso, formato)`` dell'export: l'estensione scritta dall'utente
    vince sul filtro scelto; senza estensione decide il filtro."""
    basso = str(percorso).lower()
    for fmt in en.EXPORT_FORMATS + ("pdf",):
        if basso.endswith("." + fmt):
            return str(percorso), fmt
    filtro = str(filtro).lower()
    fmt = "pdf" if "pdf" in filtro else ("docx" if "docx" in filtro else "html")
    return str(percorso) + "." + fmt, fmt


def _bases():
    """Le cartelle delle anteprime e delle ridotte del progetto aperto."""
    from . import em_matrix_panel
    return em_matrix_panel.thumb_base(), em_matrix_panel.resize_base()


def _media_of_factory(stato, grafi):
    """``media_of(ref)`` per :func:`em_narrative.chapter_html`: le anteprime
    locali dell'unità, al massimo due, con il nome del media come
    didascalia. Niente database o anteprime remote → niente immagini."""
    if not stato.conn:
        return None
    thumb, resize = _bases()
    if not thumb or not os.path.isdir(thumb):
        return None
    nodi = {n.node_id: n for g in grafi.values() for n in getattr(g, "nodes", []) or []}

    def media_of(ref):
        if ref in stato.media_cache:
            return stato.media_cache[ref]
        nodo = nodi.get(ref)
        voci = []
        if nodo is not None:
            for percorso in en.unit_media_files(stato.conn, nodo, thumb, resize, prefer="thumb"):
                nome = os.path.splitext(os.path.basename(percorso))[0]
                nome = nome.split("_", 1)[1] if "_" in nome else nome
                voci.append((percorso, nome.replace("_thumb", "")))
        stato.media_cache[ref] = voci
        return voci
    return media_of


def stop_generation(widget) -> None:
    """Ferma il thread e aspetta che esca: distruggere un QThread in corsa
    è un errore fatale di Qt, e il pannello si chiude allo scarico del
    plugin (revisione 2026-10-12). Il capitolo in corso finisce, poi si
    esce; se dopo un minuto il modello non ha risposto, si tronca."""
    stato = getattr(widget, "_stato", None)
    if stato is None or not _running(stato):
        if stato is not None:
            stato.thread = None
        return
    t = stato.thread
    try:
        t.cancel()
        if not t.wait(60_000) and t.isRunning():
            t.terminate()
            t.wait()
    except RuntimeError:
        pass
    stato.thread = None


_AZIONI = ("genera", "rigenera", "convalida", "prepara", "mappa", "esporta", "emstudio")


def build_tab(parent, iface) -> QWidget:
    """La scheda, vuota: ``show_file`` la punta su un em.json."""
    en.set_language(_lang())
    w = QWidget(parent)
    w.setObjectName("narrativa")
    stato = _State()
    stato.iface = iface
    w._stato = stato                                # noqa: SLF001 (vive col widget)
    colonna = QVBoxLayout(w)
    colonna.setContentsMargins(0, 0, 0, 0)

    etichetta_stato = QLabel("", w)
    etichetta_stato.setObjectName("stato")
    etichetta_stato.setWordWrap(True)
    colonna.addWidget(etichetta_stato)

    vuoto = QLabel("", w)
    vuoto.setObjectName("vuoto")
    vuoto.setWordWrap(True)
    vuoto.setVisible(False)
    colonna.addWidget(vuoto)

    capitoli = QListWidget(w)
    capitoli.setObjectName("capitoli")
    colonna.addWidget(capitoli, 2)

    testo = QTextBrowser(w)
    testo.setObjectName("testo")
    # I nomi delle unità sono link «unit:<id>»: un clic le evidenzia sulla
    # mappa, non apre niente.
    testo.setOpenLinks(False)
    testo.setOpenExternalLinks(False)
    colonna.addWidget(testo, 3)

    avanzamento = QLabel("", w)
    avanzamento.setObjectName("avanzamento")
    avanzamento.setVisible(False)
    colonna.addWidget(avanzamento)

    # La lingua in cui l'AI scrive: la sceglie chi scrive. Parte da quella
    # della narrativa del file (TempluMare è in inglese) o da quella di QGIS
    # (Enzo, 17 ottobre 2026: «me li scrive in inglese»).
    riga_lingua = QHBoxLayout()
    etichetta_lingua = QLabel(_t("language"), w)
    lingua = QComboBox(w)
    lingua.setObjectName("lingua")
    for codice, nome in _LINGUE:
        lingua.addItem(nome, codice)
    lingua.setToolTip(_t("language_tip"))
    etichetta_lingua.setToolTip(_t("language_tip"))
    riga_lingua.addWidget(etichetta_lingua)
    riga_lingua.addWidget(lingua, 1)
    colonna.addLayout(riga_lingua)

    def _proponi_lingua(contenitore):
        if stato.lingua_di == stato.path:
            return                                  # la scelta di chi scrive resta
        stato.lingua_di = stato.path
        codice = None
        for g in (getattr(contenitore, "graphs", {}) or {}).values():
            n = en.narrative_of(g)
            if n is not None and (n.data or {}).get("lang"):
                codice = str(n.data["lang"])[:2].lower()
                break
        for scelta in (codice, _lang(), "en"):
            i = lingua.findData(scelta) if scelta else -1
            if i >= 0:
                lingua.setCurrentIndex(i)
                return

    bottoni = {}
    riga1, riga2 = QHBoxLayout(), QHBoxLayout()
    for nome, chiave, riga in (("genera", "generate", riga1), ("rigenera", "regenerate", riga1),
                               ("convalida", "endorse", riga1), ("prepara", "prepare", riga2),
                               ("mappa", "map", riga2),
                               ("esporta", "export", riga2), ("emstudio", "emstudio", riga2),
                               ("annulla", "cancel", riga2)):
        b = QPushButton(_t(chiave), w)
        b.setObjectName(nome)
        riga.addWidget(b)
        bottoni[nome] = b
    bottoni["annulla"].setVisible(False)
    colonna.addLayout(riga1)
    colonna.addLayout(riga2)

    def _barra(livello, messaggio):
        _say(iface, livello, messaggio)

    def _scelta() -> Optional[en.ChapterView]:
        i = capitoli.currentRow()
        return stato.views[i] if 0 <= i < len(stato.views) else None

    def _pannello():
        from . import em_matrix_panel
        return em_matrix_panel

    def _mostra_scelta():
        v = _scelta()
        testo.setHtml(v.html if v else "")
        bottoni["rigenera"].setEnabled(bool(v and v.can_generate and stato.config is not None
                                            and stato.thread is None))
        ids = list(v.unit_ids) if v else []
        # `stato.thread is None` come Rigenera: `_running` dice ancora no
        # prima di `start()` (agente dei tutorial, 2026-10-12).
        bottoni["mappa"].setEnabled(bool(ids) and stato.thread is None
                                    and _pannello().can_highlight(ids))

    def _aggiorna_bottoni():
        ha_file = stato.path is not None
        ha_narrativa = bool(stato.views)
        ha_ai = stato.config is not None
        occupato = stato.thread is not None
        for nome, acceso in (("genera", ha_file and ha_ai),
                             ("prepara", ha_file),
                             ("convalida", ha_narrativa),
                             ("esporta", ha_narrativa),
                             ("mappa", False),             # lo accende _mostra_scelta
                             ("emstudio", ha_file)):
            bottoni[nome].setEnabled(bool(acceso) and not occupato)
        bottoni["annulla"].setVisible(occupato)
        avanzamento.setVisible(occupato)
        _mostra_scelta()

    def _ricarica():
        capitoli.clear()
        stato.views = []
        vuoto.setVisible(False)
        if not stato.path:
            _aggiorna_bottoni()
            return
        try:
            contenitore, _ = en.load_project(stato.path)
        except en.NarrativeError as e:
            etichetta_stato.setText(str(e))
            stato.path = None
            _aggiorna_bottoni()
            return
        grafi = getattr(contenitore, "graphs", {}) or {}
        _proponi_lingua(contenitore)
        stato.media_cache = {}
        stato.views = en.overview(contenitore, _lang(), media_of=_media_of_factory(stato, grafi))
        piu_grafi = len(grafi) > 1
        for v in stato.views:
            parola = en.status_word(v.status, _lang())
            if v.truncated:
                parola += ", " + en.msg("truncated")
            prefisso = "[%s] " % str(v.graph_id).split("|")[-1] if piu_grafi else ""
            capitoli.addItem(QListWidgetItem("%s%s — %s" % (prefisso, v.title, parola)))
        if not stato.views:
            quanti = sum(en.count_possible_chapters(g) for g in grafi.values())
            vuoto.setText(_t("empty", n=quanti))
            vuoto.setVisible(True)
        _aggiorna_bottoni()

    def _avvia(anchors=None):
        if stato.thread is not None or stato.config is None or not stato.path:
            return
        cfg, _scope = stato.config
        t = NarrativeThread(stato.path, cfg, _lang(), anchors=anchors, parent=w,
                            write_lang=lingua.currentData())
        stato.thread = t

        def _progresso(i, n, titolo):
            avanzamento.setText(_t("progress", i=i, n=n, title=titolo))

        def _fine(ok, messaggio):
            stato.thread = None
            _ricarica()
            _barra("info" if ok else "warn", messaggio)
        t.progress.connect(_progresso)
        t.finished_ok.connect(_fine)
        t.finished.connect(t.deleteLater)           # un thread per giro, nessuno in giro dopo
        avanzamento.setText(_t("starting"))
        _aggiorna_bottoni()
        t.start()

    def _genera():
        _avvia(None)

    def _rigenera():
        v = _scelta()
        if v is not None and v.can_generate:
            _avvia([(v.graph_id, v.anchor)])        # solo il grafo del capitolo scelto

    def _annulla():
        if stato.thread is not None:
            stato.thread.cancel()

    def _prepara():
        if not stato.path:
            return
        try:
            contenitore, _ = en.load_project(stato.path)
        except Exception as e:                      # noqa: BLE001
            _barra("warn", str(e))
            return
        grafi = list(contenitore.graphs.values())
        # La narrativa che il file porta di suo (TempluMare): i capitoli di
        # pyArchInit si aggiungono solo se lo si vuole, e lo si chiede ogni volta.
        del_file = [g for g in grafi if en.needs_template_choice(g)]
        if del_file:
            quanti = sum(len(en.narrative_of(g).chapters) for g in del_file)
            scelta = _chiedi_capitoli(w, quanti)
            if scelta is None:
                return
            if scelta == "file":
                _barra("info", _t("kept_file", n=quanti))
                return
        try:
            n = 0
            for g in grafi:
                n += len(en.scaffold(g, _lang(), write_lang=lingua.currentData()).chapters)
            en.save_project(contenitore, stato.path)
        except Exception as e:                      # noqa: BLE001
            _barra("warn", str(e))
            return
        _ricarica()
        _barra("info", _t("prepared", n=n))

    def _convalida():
        v = _scelta()
        menu = QMenu(w)
        azione_capitolo = menu.addAction(_t("endorse_chapter"))
        azione_capitolo.setEnabled(v is not None and v.status == "ai_draft")
        azione_tutti = menu.addAction(_t("endorse_all"))
        scelta = _exec(menu, bottoni["convalida"].mapToGlobal(
            bottoni["convalida"].rect().bottomLeft()))
        if scelta is None:
            return
        solo_capitolo = scelta is azione_capitolo
        try:
            contenitore, _ = en.load_project(stato.path)
        except en.NarrativeError as e:
            _barra("warn", str(e))
            return
        grafi = list(contenitore.graphs.items())
        autori = []
        for _gid, g in grafi:
            autori.extend(a for a in en.human_authors(g) if a not in autori)
        nomi = [nome for _id, nome in autori]
        nome, ok = QInputDialog.getItem(w, _t("endorse"), _t("who"), nomi, 0, True)
        if not ok or not str(nome).strip():
            return
        firmati = 0
        for gid, g in grafi:
            narrativa = en.narrative_of(g)
            if narrativa is None:
                continue
            if solo_capitolo and v is not None and v.graph_id != gid:
                continue
            if not narrativa.pending_validation():
                continue                            # niente da firmare: nessun autore in più
            autore = en.add_author(g, str(nome))
            try:
                firmati += en.endorse(g, narrativa, autore,
                                      anchor=v.anchor if solo_capitolo else None)
            except Exception as e:                  # noqa: BLE001
                _barra("warn", str(e))
                return
        if not firmati:
            _barra("info", _t("nothing_to_endorse"))
            return
        try:
            en.save_project(contenitore, stato.path)
        except en.NarrativeError as e:
            _barra("warn", str(e))
            return
        _ricarica()
        _barra("info", _t("endorsed", n=firmati, who=nome))

    def _esporta():
        if not stato.path:
            return
        base = stato.path
        for estensione in (".em.json", ".json"):
            if base.lower().endswith(estensione):
                base = base[:-len(estensione)]
                break
        # Il nome proposto è senza estensione: così decide il filtro scelto
        # (con «.html» proposto, «PDF stampabile» scriveva un HTML).
        percorso, filtro = QFileDialog.getSaveFileName(
            w, _t("export"), base + "_narrativa", _t("export_filter"))
        if not percorso:
            return
        percorso, fmt = export_target(percorso, filtro)
        try:
            contenitore, _ = en.load_project(stato.path)
            thumb, resize = _bases()
            scritti = []
            for gid, g in contenitore.graphs.items():
                narrativa = en.narrative_of(g)
                if narrativa is None:
                    continue
                destinazione = percorso
                if len(contenitore.graphs) > 1:
                    radice, est = os.path.splitext(percorso)
                    destinazione = "%s_%s%s" % (radice, str(gid).split("|")[-1], est)
                # Le foto delle unità citate, quando il database e i file ci sono.
                try:
                    figure = en.figures_for(g, narrativa, stato.conn, thumb, resize)
                except Exception:                   # noqa: BLE001
                    figure = {}
                if fmt == "pdf":
                    scritti.append(en.export_pdf(g, narrativa, destinazione, figures=figure,
                                                 lang=_lang()))
                else:
                    scritti.append(en.export_file(g, narrativa, fmt, destinazione,
                                                  figures=figure, map_conn=stato.conn,
                                                  lang=_lang(), media_base=(thumb, resize)))
        except Exception as e:                      # noqa: BLE001
            _barra("warn", str(e))
            return
        _barra("info", _t("exported", path=", ".join(scritti)))

    def _evidenzia(ids):
        quante, messaggio = _pannello().highlight(stato.iface, list(ids), _lang())
        _barra("info" if quante else "warn", messaggio)

    def _mappa():
        v = _scelta()
        if v is not None and v.unit_ids:
            _evidenzia(v.unit_ids)

    def _apri_unita(url):
        """Il clic su un nome nel testo: ``unit:<id>`` evidenzia quell'unità."""
        try:
            if url.scheme() != "unit":
                return
            ref = unquote(url.path() or url.toString()[len("unit:"):])
        except Exception:                           # noqa: BLE001
            return
        if ref:
            _evidenzia([ref])

    def _emstudio():
        if not stato.path:
            return
        from . import em_export
        if not em_export.open_in_emstudio(stato.path):
            _barra("warn", _t("emstudio_missing"))

    capitoli.currentRowChanged.connect(lambda _i: _mostra_scelta())
    bottoni["genera"].clicked.connect(_genera)
    bottoni["rigenera"].clicked.connect(_rigenera)
    bottoni["convalida"].clicked.connect(_convalida)
    bottoni["prepara"].clicked.connect(_prepara)
    bottoni["esporta"].clicked.connect(_esporta)
    bottoni["emstudio"].clicked.connect(_emstudio)
    bottoni["mappa"].clicked.connect(_mappa)
    bottoni["annulla"].clicked.connect(_annulla)
    testo.anchorClicked.connect(_apri_unita)
    w._ricarica = _ricarica                         # noqa: SLF001
    w._apri_unita = _apri_unita                     # noqa: SLF001 (per le prove)
    _aggiorna_bottoni()
    return w


def show_file(widget, path, conn_str=None) -> None:
    """Punta la scheda sul file e la ricarica (anche a ogni riapertura
    del pannello su un altro sito). ``conn_str`` è il database del
    progetto: serve per le immagini delle unità."""
    stato: _State = widget._stato                   # noqa: SLF001
    if _running(stato):
        # Cambiare file sotto un thread che poi salva riscriverebbe il
        # nuovo export con il grafo di prima.
        _say(stato.iface, "warn", _t("busy"))
        return
    stato.path = str(path) if path else None
    stato.conn = conn_str or None
    stato.config = en.llm_config()
    etichetta = widget.findChild(QLabel, "stato")
    if stato.config is None:
        etichetta.setText(_t("no_ai"))
    else:
        cfg, scope = stato.config
        etichetta.setText(en.describe_config(cfg, scope, _lang()) + " · " + _t("close_emstudio"))
    widget._ricarica()                              # noqa: SLF001
