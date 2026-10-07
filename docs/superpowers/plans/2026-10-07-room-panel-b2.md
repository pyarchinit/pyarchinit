# B2 pieno — la stanza dentro pyArchInit (pannello web del nodo) — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** la pagina per-stanza del nodo StratiGraph («l'indirizzo stabile per stanza», `/em/work/?room=<id>`) si apre in un **pannello dentro pyArchInit** (QWebEngineView in un QDockWidget), col browser di sistema come ripiego quando Qt WebEngine manca — il B2 che Emanuel descrive, nella forma che il nodo REALE serve oggi.

**Architecture:** un modulo Qt nuovo e piccolo (`modules/s3dgraphy/room/room_panel.py`: dock + WebEngine via il pattern `_import_qt_webengine` già in `tabs/DemPlotDialogs.py`), un costruttore d'indirizzo puro in `room_client.py` (`room_work_url`, stessa logica di base ±`/em` di `rooms_door`), e il ricablaggio di «Apri il nodo (stanze)…»: con una stanza configurata si apre LA stanza nel pannello, senza si apre la porta del nodo; in entrambi i casi, niente WebEngine → browser. Un pannello per sessione: riaprire sostituisce il contenuto, mai un secondo dock.

**Tech Stack:** Qt (QDockWidget + QWebEngineView con fallback), urllib per la sonda (già nel client, 5 s); niente dipendenze nuove. GPL: il pannello CARICA una pagina via HTTP dal nodo (GPL-3) — nessun codice loro nel plugin.

**Spec:** `docs/superpowers/specs/2026-10-07-one-bridge-s3dgraphy-design.md` §5 (B2) + Addendum C; messaggio di Emanuel 2026-10-07 («la strada più semplice è aprire nel pannello la versione web … puntata sulla stanza del sito, in sola lettura»).

**Fatti misurati che il piano usa (2026-10-07):**
- l'indirizzo per-stanza è `?room=<id>` sulla pagina *work* (`app/rooms_ui/rooms.js:1745`: «`/em/work/?room=<id>` is the stable per-room address»); sul nodo nudo risponde `GET /rooms/work/?room=…` → 200 (misurato sul locale :8020);
- l'editor/reader di EMStudio (`/em/studio/`, `/em/read/`) è un QUARTO repo servito solo dai nodi che lo montano: il pannello punta alla pagina del NODO, che c'è sempre; quando un nodo istituzionale servirà EMStudio, l'indirizzo resta sotto la stessa base e il pannello non cambia;
- la sola-lettura è del SERVER (ruolo viewer): il pannello non deve fingerla lato client;
- Qt WebEngine può mancare in un profilo QGIS: `tabs/DemPlotDialogs.py:_import_qt_webengine()` è il pattern di casa (Qt5/Qt6, None se assente).

## Global Constraints

- Branch: feature branch `room-panel` da `Stratigraph_00001`; merge solo alla release. Mai `master`.
- Suite canonica (identica ai piani precedenti, dal checkout in prova): `QT_QPA_PLATFORM=offscreen PYARCHINIT_HOME=/Users/enzo/pyarchinit_5 PYTHONPATH=/Applications/QGIS.app/Contents/Resources/python /Applications/QGIS.app/Contents/MacOS/bin/python3 -m pytest tests/sync -q --continue-on-collection-errors --ignore=tests/sync/test_groups_dialog_smoke.py --ignore=tests/sync/test_paradata_dialog_smoke.py`. Baseline: 0 fail, 1 xfail, 7 error ambientali; il test vivo si salta senza nodo.
- **MAI istanziare QWebEngineView nei test** (i due smoke ignorati della suite sono crash Qt noti): i test del pannello sono guardie sul sorgente + logica pura; il collaudo visivo è di Enzo in QGIS.
- Nodo locale per il collaudo: `EM_SERVER_ALLOW_ANON=1 ~/stratigraph-node/venv/bin/uvicorn app.main:app --port 8020` da `~/stratigraph-node/stratigraph-server`.
- Commit `feat:`/`test:` senza AI-attribution (regola utente). Release: `metadata.txt` → `5.13.32-alpha`, changelog IT+EN, tag `room-panel-5.13.32-alpha`, GitHub pre-release, api-docs RTD, tutorial (it/en/pt/ro/el: il paragrafo «Apri il nodo» impara il pannello).

## Review Focus

1. **WebEngine assente** → browser di sistema, mai un'eccezione, e l'utente lo viene a sapere (messageBar, non un dialogo bloccante). → Task 2/3.
2. **Nodo muto** quando si apre il pannello → la sonda ha già il timeout di 5 s; l'URL si costruisce comunque (il pannello mostrerà l'errore del browser engine, non un gelo di QGIS). → Task 1 (il builder non solleva su nodo muto).
3. **Stanza con spazi/UTF-8 nell'id** → `?room=` quotato. → Task 1.
4. **Doppio clic sulla voce di menu** → UN pannello (il dock esistente si riusa e si riporta davanti), mai due. → Task 2.
5. **Reload del plugin** → il dock viene rimosso in `unload()` (la lezione del 5.13.29). → Task 3.

---

### Task 0: Worktree e baseline

- [ ] **Step 1:**

```bash
PLUGIN="/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit"
git -C "$PLUGIN" worktree add -b room-panel /Users/enzo/pyarchinit-room-panel Stratigraph_00001
cp -R "$PLUGIN/ext_libs" /Users/enzo/pyarchinit-room-panel/ext_libs
```

- [ ] **Step 2:** suite canonica dal worktree. Expected: `0 failed` (1 xfail, 7 error noti; il live si salta o passa col nodo acceso).
- [ ] **Step 3:** nessun commit (niente è cambiato): il task produce solo il worktree.

### Task 1: `room_work_url` — l'indirizzo della stanza (TDD, puro)

**Files:**
- Modify: `modules/s3dgraphy/room/room_client.py`
- Test: `tests/sync/test_room_client.py` (estendere), `tests/sync/test_room_delivery_live.py` (estendere)

**Interfaces:**
- Consumes: la logica di base di `rooms_door` (già esistente: base ±`/em`, sonda `_probe_http`).
- Produces: `room_work_url(server_url, room_id, http=_probe_http) -> str` — l'URL della pagina *work* della stanza: `<base>/em/work/?room=<id>` dietro Caddy, `<base>/rooms/work/?room=<id>` sul nodo nudo; `room_id` quotato; su nodo muto restituisce comunque il candidato Caddy (mai un'eccezione: il pannello mostrerà il suo errore).

- [ ] **Step 1: Test rossi** (in coda a `tests/sync/test_room_client.py`):

```python
def test_room_work_url_points_at_the_stable_per_room_address(monkeypatch):
    """B2: «/em/work/?room=<id>» è l'indirizzo stabile per stanza
    (rooms_ui/rooms.js:1745); sul nodo nudo la stessa pagina vive sotto
    /rooms/work/. L'id viaggia quotato."""
    from modules.s3dgraphy.room import room_client

    def bare(method, url, payload, token):
        return (200, {}) if "/rooms/work/" in url and "/em/" not in url \
            else (404, {})

    url = room_client.room_work_url("http://x", "scavo 2026/α", http=bare)
    assert url == "http://x/rooms/work/?room=scavo%202026%2F%CE%B1"

    def caddy(method, url, payload, token):
        return (200, {}) if "/em/work/" in url else (404, {})

    url = room_client.room_work_url("http://x", "r1", http=caddy)
    assert url == "http://x/em/work/?room=r1"


def test_room_work_url_never_raises_on_a_mute_node(monkeypatch):
    from modules.s3dgraphy.room import room_client

    def dead(method, url, payload, token):
        raise OSError("no route to host")

    url = room_client.room_work_url("http://x", "r1", http=dead)
    assert url.endswith("/em/work/?room=r1")
```

- [ ] **Step 2: Run — FAIL** (`AttributeError: room_work_url`). Run: `pytest tests/sync/test_room_client.py -q` (env canonico).

- [ ] **Step 3: Implementazione** (in `room_client.py`, accanto a `rooms_door`):

```python
def room_work_url(server_url, room_id, http: Http = _probe_http):
    """L'indirizzo stabile della stanza: la pagina *work* del nodo.

    `/em/work/?room=<id>` dietro Caddy, `/rooms/work/?room=<id>` sul nodo
    nudo (rooms_ui/rooms.js:1745). Su nodo muto si restituisce comunque il
    candidato Caddy: il pannello mostrerà il SUO errore — mai un'eccezione
    qui, e mai più di due sonde da 5 s (Review Focus 2).
    """
    import urllib.parse
    base = server_url.rstrip("/")
    query = "?room=%s" % urllib.parse.quote(room_id, safe="")
    paths = ("/work/",) if base.endswith("/em") \
        else ("/em/work/", "/rooms/work/")
    for path in paths:
        try:
            status, _body = http("GET", base + path, None, "")
        except Exception:
            continue
        if status == 200:
            return base + path + query
    return base + ("/work/" if base.endswith("/em") else "/em/work/") + query
```

- [ ] **Step 4: Run — PASS** (i 2 nuovi + i 17 esistenti del file).

- [ ] **Step 5: Estendere il test vivo** (in coda a `tests/sync/test_room_delivery_live.py`):

```python
def test_the_room_work_page_answers(room):
    from modules.s3dgraphy.room import room_client
    url = room_client.room_work_url(NODE, room)
    assert "/rooms/work/?room=" in url
    with urllib.request.urlopen(url, timeout=5) as r:
        assert r.status == 200
```

Run (nodo acceso): `pytest tests/sync/test_room_delivery_live.py -q`. Expected: `3 passed`.

- [ ] **Step 6: Commit** — `feat(room): room_work_url — l'indirizzo stabile della stanza, base ±/em, id quotato`

### Task 2: il pannello (QDockWidget + WebEngine, ripiego nel browser)

**Files:**
- Create: `modules/s3dgraphy/room/room_panel.py`
- Test: `tests/sync/test_room_panel.py` (nuovo — SOLO guardie sorgente/logica, mai istanze Qt WebEngine)

**Interfaces:**
- Consumes: `tabs/DemPlotDialogs._import_qt_webengine()` (pattern di casa, Qt5/Qt6 → classe o None).
- Produces: `open_in_panel(iface, url, title) -> bool` — True = pannello aperto/riusato; False = WebEngine assente (il chiamante ripiega sul browser); `PANEL_OBJECT_NAME = "pyarchinitRoomPanel"`; `close_panel(iface) -> None` (per `unload()`).

- [ ] **Step 1: Test rossi** — `tests/sync/test_room_panel.py` (intero):

```python
"""Il pannello della stanza: guardie sul sorgente, mai istanze WebEngine
(i due smoke ignorati della suite sono crash Qt noti — Global Constraints).
"""
from __future__ import annotations

from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parents[2]
SRC = (PLUGIN_ROOT / "modules" / "s3dgraphy" / "room"
       / "room_panel.py")


def test_the_panel_module_exists_and_exposes_the_contract():
    src = SRC.read_text(encoding="utf-8")
    for name in ("def open_in_panel", "def close_panel",
                 "PANEL_OBJECT_NAME"):
        assert name in src, name


def test_webengine_comes_from_the_house_pattern_and_may_be_absent():
    """Qt WebEngine può mancare: si usa _import_qt_webengine (Qt5/Qt6,
    None se assente) e open_in_panel risponde False, mai un raise."""
    src = SRC.read_text(encoding="utf-8")
    assert "_import_qt_webengine" in src
    assert "return False" in src


def test_one_panel_per_session():
    """Review Focus 4: riaprire RIUSA il dock (objectName fisso), mai due."""
    src = SRC.read_text(encoding="utf-8")
    assert "findChild" in src or "findChildren" in src
    assert "raise_" in src
```

- [ ] **Step 2: Run — FAIL** (file assente). Expected: 3 FAILED/errors.

- [ ] **Step 3: Implementazione** — `room_panel.py` (intero):

```python
"""La stanza dentro pyArchInit: un dock col web del nodo (B2).

Il pannello CARICA una pagina servita dal nodo via HTTP — nessun codice di
EMStudio o del server entra nel plugin (GPL-2 qui, GPL-3 là: aggregazione).
La sola-lettura è del SERVER (ruolo viewer): qui non si finge nulla.
Qt WebEngine può mancare in un profilo QGIS: allora si risponde False e il
chiamante apre il browser — mai un'eccezione per una finestra.
"""
from __future__ import annotations

PANEL_OBJECT_NAME = "pyarchinitRoomPanel"


def _webengine():
    try:
        try:
            from tabs.DemPlotDialogs import _import_qt_webengine
        except ImportError:
            # plugin importato come pacchetto: room/ → s3dgraphy → modules
            # → root = quattro livelli
            from ....tabs.DemPlotDialogs import _import_qt_webengine  # noqa
        return _import_qt_webengine()
    except Exception:
        return None


def _existing(iface):
    try:
        main = iface.mainWindow()
        from qgis.PyQt.QtWidgets import QDockWidget
        return main.findChild(QDockWidget, PANEL_OBJECT_NAME)
    except Exception:
        return None


def open_in_panel(iface, url, title):
    """Apri (o riusa) il pannello sul `url`. False = niente WebEngine."""
    view_class = _webengine()
    if view_class is None:
        return False
    try:
        from qgis.PyQt.QtCore import Qt, QUrl
        from qgis.PyQt.QtWidgets import QDockWidget

        dock = _existing(iface)
        if dock is None:
            dock = QDockWidget(title, iface.mainWindow())
            dock.setObjectName(PANEL_OBJECT_NAME)
            view = view_class(dock)
            dock.setWidget(view)
            iface.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, dock)
        else:
            dock.setWindowTitle(title)
            view = dock.widget()
        view.load(QUrl(url))
        dock.show()
        dock.raise_()
        return True
    except Exception:
        # una finestra che non si apre non è un motivo per un traceback
        return False


def close_panel(iface):
    """Per unload(): il dock non deve sopravvivere al plugin (lezione
    della 5.13.29 — le voci duplicate al reload)."""
    dock = _existing(iface)
    if dock is not None:
        try:
            iface.removeDockWidget(dock)
            dock.deleteLater()
        except Exception:
            pass
```

> Nota per l'esecutore: il doppio import di `_import_qt_webengine` va VERIFICATO a runtime offscreen (`python -c "from modules.s3dgraphy.room.room_panel import _webengine; print(_webengine())"` dall'ambiente canonico): se il relativo a 4 punti non risolve nel layout reale, tenere SOLO l'assoluto con try/except → None — il contratto resta «classe o None, mai un raise», e il test di fallback è il giudice.

- [ ] **Step 4: Run — PASS** (3 passed) + `python3 -m py_compile modules/s3dgraphy/room/room_panel.py`.
- [ ] **Step 5: Commit** — `feat(room): il pannello della stanza — dock WebEngine riusabile, False senza WebEngine (B2)`

### Task 3: «Apri il nodo» impara il pannello; `unload()` lo chiude

**Files:**
- Modify: `pyarchinitPlugin.py` (`_open_rooms_door`, `unload()`)
- Test: `tests/sync/test_room_panel.py` (estendere)

**Interfaces:**
- Consumes: `room_client.NodeSettings`, `room_client.rooms_door`, `room_client.room_work_url`, `room_panel.open_in_panel`, `room_panel.close_panel`.
- Produces: con `room_id` configurata → pannello sulla **stanza** (`room_work_url`); senza → pannello sulla **porta** (`rooms_door`); `open_in_panel` False → `webbrowser.open` + un messaggio nella messageBar («Qt WebEngine assente: aperto nel browser»).

- [ ] **Step 1: Guardie rosse** (in coda a `tests/sync/test_room_panel.py`):

```python
def test_the_menu_opens_the_room_in_the_panel_with_a_browser_fallback():
    src = (PLUGIN_ROOT / "pyarchinitPlugin.py").read_text(encoding="utf-8")
    body = src.split("def _open_rooms_door", 1)[1].split("\n    def ", 1)[0]
    assert "room_work_url" in body, "con una stanza configurata si apre LA stanza"
    assert "open_in_panel" in body
    assert "webbrowser" in body, "niente WebEngine → browser"
    assert "messageBar" in body


def test_unload_closes_the_panel():
    import re
    src = (PLUGIN_ROOT / "pyarchinitPlugin.py").read_text(encoding="utf-8")
    unload = re.search(r"def unload\(self\):(.*?)\n    def ", src, re.S)
    assert unload and "close_panel" in unload.group(1)
```

- [ ] **Step 2: Run — FAIL** (2 FAILED).

- [ ] **Step 3: Ricablaggio.** Il corpo nuovo di `_open_rooms_door`:

```python
    def _open_rooms_door(self):
        """B2: la stanza (o la porta del nodo) dentro pyArchInit; browser
        come ripiego quando Qt WebEngine manca nel profilo."""
        import webbrowser
        from qgis.PyQt.QtWidgets import QMessageBox
        from modules.s3dgraphy.room import room_client, room_panel

        settings = room_client.NodeSettings()
        if not settings.server_url:
            QMessageBox.information(
                self.iface.mainWindow(), "Nodo StratiGraph",
                "Nessun nodo configurato: consegna prima un sito (la "
                "finestra chiede l'indirizzo) o imposta %s."
                % room_client.SERVER_URL_VARIABLE)
            return
        try:
            if settings.room_id:
                url = room_client.room_work_url(settings.server_url,
                                                settings.room_id)
                title = "Stanza «%s»" % settings.room_id
            else:
                url = room_client.rooms_door(settings.server_url)
                title = "Nodo StratiGraph"
        except Exception:
            url = settings.server_url + "/em/rooms/"
            title = "Nodo StratiGraph"
        if not room_panel.open_in_panel(self.iface, url, title):
            webbrowser.open(url)
            try:
                self.iface.messageBar().pushInfo(
                    "Stanza", "Qt WebEngine assente in questo profilo: "
                              "aperto nel browser.")
            except Exception:
                pass
```

In `unload()`, accanto alla rimozione delle voci di menu:

```python
        try:
            from modules.s3dgraphy.room import room_panel
            room_panel.close_panel(self.iface)
        except Exception:
            pass
```

- [ ] **Step 4: Run — PASS** (`pytest tests/sync/test_room_panel.py tests/sync/test_room_client.py -q` tutto verde) + `py_compile pyarchinitPlugin.py`.
- [ ] **Step 5: Collaudo a mano (Enzo, in QGIS):** nodo acceso, stanza `collaudo-scavo-archeologico` configurata → «Apri il nodo (stanze)…» apre il dock sulla pagina della stanza; secondo clic = stesso dock davanti; reload plugin = dock sparito.
- [ ] **Step 6: Commit** — `feat(room): «Apri il nodo» apre la stanza nel pannello (B2), browser come ripiego, dock chiuso in unload`

### Task 4: release e satelliti

**Files:**
- Modify: `metadata.txt` (→ `5.13.32-alpha`), `dev_logs/CHANGELOG.md`, tutorial it/en/pt/ro/el (`01_configurazione.md`)

- [ ] **Step 1: Tutorial** — nelle 5 lingue, la frase finale della sezione stanza («Con Extended Matrix → Apri il nodo…») impara il pannello: *si apre **dentro pyArchInit** (pannello laterale) quando Qt WebEngine è disponibile, altrimenti nel browser; con una stanza configurata si apre direttamente la pagina della stanza.*
- [ ] **Step 2: Suite canonica + sweep → ≤ baseline. Changelog IT+EN** (cosa apre, il ripiego, un pannello per sessione, la sola-lettura è del server).
- [ ] **Step 3: Merge ff su `Stratigraph_00001`; tag `room-panel-5.13.32-alpha`; push; GitHub pre-release; api-docs RTD; rimozione worktree.**
- [ ] **Step 4: Memoria** — `project_stratigraph_node_local.md`: B2 shipped, cosa resta per il B2 «EMStudio vero» (il reader `/em/read/` quando un nodo lo monta — nessun cambio nostro: stessa base, stesso pannello).
