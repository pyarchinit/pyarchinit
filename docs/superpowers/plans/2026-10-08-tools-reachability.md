# Strumenti raggiungibili: un motore web di ripiego + EMStudio che si installa da sé — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Che il pannello della stanza si apra anche dove manca Qt WebEngine, e che chi non ha EMStudio lo possa installare dal menu, su Mac, Windows e Linux.

**Architecture:** Due pezzi indipendenti. (1) Il pannello sceglie il motore a scaletta: `QWebEngineView` se c'è, altrimenti `QWebView` di **QtWebKit** — che su questo profilo QGIS 3 c'è e la pagina della stanza la rende (verificato: titolo e corpo dell'app arrivano, nessun errore JS) — altrimenti il browser, come già fa. (2) Un installatore legge le release di EMStudio dall'API GitHub, scegli l'artefatto del sistema in uso, lo scarica verificando lo `sha256` che l'API dichiara, lo installa in una cartella nostra e lo lancia. Nessun codice EMStudio entra nel plugin: si scarica il binario ufficiale su richiesta dell'utente e lo si esegue come processo separato — il confine GPL resta quello di oggi.

**Tech Stack:** Python 3.9 (QGIS), PyQt5 (QtWebEngineWidgets / QtWebKitWidgets), `urllib.request`, `tarfile`, API GitHub REST, pytest.

**Spec:** `docs/superpowers/specs/2026-10-07-one-bridge-s3dgraphy-design.md` (Addendum C, parti B1/B2). Le misure d'ambiente stanno in «Ricognizione».

## Ricognizione (misurata il 2026-10-08)

- QGIS su questo Mac: Qt 5.15.2, PyQt 5.15.4. **`PyQt5.QtWebEngineWidgets` assente**, `PyQt5.QtWebKitWidgets` **presente**, `QtWebChannel` presente. `qgis.gui.QgsWebView` non esiste più in questa build.
- La pagina per-stanza caricata in un `QWebView` offscreen: `loadFinished ok=True`, titolo `This node · StratiGraph`, corpo reso dall'app («Sign in to see the rooms you work in…»), nessun messaggio di console. QtWebKit basta per questa pagina.
- EMStudio pubblica **solo pre-release** (`/releases/latest` risponde 404: va letto `/releases`). Gli artefatti di `v1.6.0-dev.26`: `EMStudio_aarch64.app.tar.gz` e `EMStudio_1.6.0_aarch64.dmg` (Mac ARM), `EMStudio_1.6.0_x64-setup.exe` e `.msi` (Windows), `EMStudio_1.6.0_amd64.AppImage` / `.deb` / `.rpm` (Linux). **Niente artefatto per Mac Intel.**
- L'API espone per ogni artefatto `digest: "sha256:…"`: il download si può verificare.

## Global Constraints

- **Niente righe di attribuzione AI** in commit, issue, PR, commenti.
- **Solo ramo dev `Stratigraph_00001`.**
- **Confine GPL**: niente codice EMStudio o del server dentro il plugin; download del binario ufficiale su richiesta + processo separato.
- **Mai istanziare un `QWebEngineView` (né un `QWebView`) nei test**: le guardie leggono il codice o iniettano finte fabbriche.
- Nessun segreto su disco né nei log; nessun token serve qui (API GitHub pubblica, senza autenticazione).
- Comando di test canonico: quello del piano `2026-10-08-em-fidelity-and-usv-records.md`.

## Review Focus

1. **Scaricare è un'azione verso l'esterno.** La finestra di conferma deve dire *prima*: versione, nome dell'artefatto, dimensione, indirizzo e cartella di destinazione. Un «sì» vale per quel download, non per i prossimi.
2. **Mac Intel non ha artefatto.** Il percorso deve finire in una frase chiara («questa release non pubblica un pacchetto per Mac Intel»), non in un `None` che diventa un `TypeError` tre righe sotto.
3. **Rete che non risponde.** API lenta, 403 per rate-limit, download interrotto a metà: ogni caso finisce in un messaggio, e un file incompleto non resta in giro a somigliare a un'installazione.
4. **QtWebKit non è WebEngine.** Il pannello non deve chiamare metodi che solo WebEngine ha (`setZoomFactor` c'è in entrambi, `page().profile()` no): la scaletta sceglie il motore e il resto del pannello parla solo l'API comune (`load(QUrl)`, `title()`).
5. **Digest che non torna.** Se lo `sha256` calcolato non coincide con quello dichiarato, il file si cancella e non si installa niente.

---

### Task 1: Il pannello sceglie il motore (WebEngine → WebKit → browser)

**Files:**
- Modify: `modules/s3dgraphy/room/room_panel.py`
- Test: `tests/sync/test_room_panel.py`

**Interfaces:**
- Consumes: `tabs.DemPlotDialogs._import_qt_webengine` (già usato).
- Produces: `web_view_class() -> tuple[type | None, str]` — la classe e il nome del motore (`"webengine"`, `"webkit"`, `""`).

- [ ] **Step 1: Write the failing test**

```python
def test_the_panel_falls_back_to_webkit_when_webengine_is_missing():
    """Su un profilo senza QtWebEngine il pannello usa QtWebKit, che QGIS 3
    spedisce ancora: il browser resta l'ultimo ripiego, non il primo."""
    import modules.s3dgraphy.room.room_panel as panel
    assert hasattr(panel, "web_view_class")
    src = inspect.getsource(panel.web_view_class)
    assert "QtWebKitWidgets" in src
    assert src.index("_import_qt_webengine") < src.index("QtWebKitWidgets")


def test_the_engine_name_travels_with_the_class(monkeypatch):
    import modules.s3dgraphy.room.room_panel as panel

    class _Fake:
        pass

    monkeypatch.setattr(panel, "_webengine", lambda: None)
    monkeypatch.setattr(panel, "_webkit", lambda: _Fake)
    assert panel.web_view_class() == (_Fake, "webkit")
    monkeypatch.setattr(panel, "_webkit", lambda: None)
    assert panel.web_view_class() == (None, "")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `… -m pytest tests/sync/test_room_panel.py -q`
Expected: FAIL — `AttributeError: module … has no attribute 'web_view_class'`.

- [ ] **Step 3: Write minimal implementation**

In `modules/s3dgraphy/room/room_panel.py`:

```python
def _webkit():
    """``QWebView`` di QtWebKit, o None.

    QGIS 3 spedisce ancora QtWebKit su macOS e Linux (misurato su questo
    profilo: Qt 5.15.2 / PyQt 5.15.4, WebEngine assente, WebKit
    presente). Il motore è vecchio ma la pagina della stanza la rende.
    """
    try:
        from PyQt5.QtWebKitWidgets import QWebView
        return QWebView
    except Exception:                               # noqa: BLE001
        try:
            from qgis.PyQt.QtWebKitWidgets import QWebView
            return QWebView
        except Exception:                           # noqa: BLE001
            return None


def web_view_class():
    """La classe della vista e il nome del motore, dal migliore al peggiore."""
    engine = _webengine()
    if engine is not None:
        return engine, "webengine"
    webkit = _webkit()
    if webkit is not None:
        return webkit, "webkit"
    return None, ""
```

e `open_in_panel` usa `web_view_class()` al posto di `_webengine()`, mettendo il nome del motore nel tooltip del pannello: `view.setToolTip("Motore: %s" % engine_name)`.

- [ ] **Step 4: Run test to verify it passes**

Run: come allo Step 2.
Expected: PASS.

- [ ] **Step 5: Collaudo vivo (fuori dai test, a mano)**

```bash
QT_QPA_PLATFORM=offscreen /Applications/QGIS.app/Contents/MacOS/bin/python3 "$SCRATCHPAD/webkit_test.py"
```
Expected: `RESULT: LOADED`, titolo `This node · StratiGraph`.

- [ ] **Step 6: Il messaggio del ripiego dice la verità**

In `pyarchinitPlugin.py::_open_rooms_door`, il messaggio del browser non deve più dare la colpa solo a WebEngine:

```python
                    "Stanza", "Nessun motore web disponibile in questo "
                              "profilo (né Qt WebEngine né Qt WebKit): "
                              "aperto nel browser.")
```

- [ ] **Step 7: Commit**

```bash
git add modules/s3dgraphy/room/room_panel.py pyarchinitPlugin.py tests/sync/test_room_panel.py
git commit -m "feat(stanza): il pannello usa QtWebKit dove manca WebEngine"
```

---

### Task 2: EMStudio si installa dal menu, su ogni piattaforma

**Files:**
- Create: `modules/s3dgraphy/em_studio_installer.py`
- Modify: `modules/s3dgraphy/em_export.py` (`_find_emstudio_executable` guarda anche nella cartella nostra)
- Modify: `pyarchinitPlugin.py` (voce di menu «Installa EMStudio…» + offerta quando manca)
- Test: `tests/sync/test_em_studio_installer.py`

**Interfaces:**
- Produces:
  - `PLATFORM_ASSETS: dict[tuple[str, str], tuple[str, ...]]` — pattern d'artefatto per `(system, machine)`
  - `pick_asset(assets, system, machine) -> dict | None`
  - `latest_release(http=_http) -> dict` (`tag`, `assets`)
  - `download_asset(asset, dest_dir, http=_http) -> Path` (verifica `digest`)
  - `install(archive, dest_dir, system=None, runner=subprocess) -> Path`
  - `install_dir() -> Path` = `pyarchinit_home() / "tools" / "EMStudio"`
  - `InstallError(Exception)`

- [ ] **Step 1: Write the failing test**

```python
ASSETS = [
    {"name": "EMStudio-1.6.0-1.x86_64.rpm", "size": 62105656,
     "digest": "sha256:0ad2", "browser_download_url": "https://x/rpm"},
    {"name": "EMStudio_1.6.0_aarch64.dmg", "size": 37735827,
     "digest": "sha256:3571", "browser_download_url": "https://x/dmg"},
    {"name": "EMStudio_1.6.0_amd64.AppImage", "size": 140102136,
     "digest": "sha256:17f1", "browser_download_url": "https://x/appimage"},
    {"name": "EMStudio_1.6.0_x64-setup.exe", "size": 39688057,
     "digest": "sha256:ea2f", "browser_download_url": "https://x/exe"},
    {"name": "EMStudio_aarch64.app.tar.gz", "size": 37458736,
     "digest": "sha256:bf3f", "browser_download_url": "https://x/tgz"},
]


def test_each_platform_gets_its_own_artefact():
    """Mac ARM preferisce il .app.tar.gz (si estrae senza montare un
    disco), Windows il setup, Linux l'AppImage (non chiede root)."""
    assert pick_asset(ASSETS, "Darwin", "arm64")["name"].endswith(".app.tar.gz")
    assert pick_asset(ASSETS, "Windows", "AMD64")["name"].endswith("-setup.exe")
    assert pick_asset(ASSETS, "Linux", "x86_64")["name"].endswith(".AppImage")


def test_mac_intel_says_there_is_no_package_instead_of_crashing():
    """La release di oggi non pubblica niente per Mac Intel: la risposta è
    None, e chi chiama lo dice a parole."""
    assert pick_asset(ASSETS, "Darwin", "x86_64") is None


def test_a_download_whose_digest_does_not_match_is_thrown_away(tmp_path):
    asset = {"name": "EMStudio_aarch64.app.tar.gz", "size": 4,
             "digest": "sha256:" + "0" * 64,
             "browser_download_url": "https://x/tgz"}
    with pytest.raises(InstallError, match="impronta"):
        download_asset(asset, tmp_path, http=lambda url, timeout=0: b"ciao")
    assert list(tmp_path.iterdir()) == []      # niente file a metà


def test_the_release_list_is_read_because_latest_is_a_prerelease():
    """EMStudio pubblica solo pre-release: /releases/latest risponde 404."""
    import modules.s3dgraphy.em_studio_installer as inst
    assert "/releases?" in inst.RELEASES_URL
    assert "/releases/latest" not in inst.RELEASES_URL
```

- [ ] **Step 2: Run test to verify it fails**

Run: `… -m pytest tests/sync/test_em_studio_installer.py -q`
Expected: FAIL — `ModuleNotFoundError: modules.s3dgraphy.em_studio_installer`.

- [ ] **Step 3: Write minimal implementation**

`modules/s3dgraphy/em_studio_installer.py`:

```python
"""Scarica e installa EMStudio, il visore dell'Extended Matrix.

Il plugin non contiene e non collega codice EMStudio (GPL-3): scarica il
binario ufficiale dalle release GitHub quando l'utente lo chiede e lo
esegue come processo separato, come già fa `em_export.open_in_emstudio`.

EMStudio pubblica SOLO pre-release, quindi `/releases/latest` risponde
404: si legge la lista e si prende la prima. Ogni artefatto porta nella
risposta dell'API il suo `digest` sha256, che qui si verifica.
"""

RELEASES_URL = ("https://api.github.com/repos/ExtendedMatrix/EMStudio"
                "/releases?per_page=5")

#: (sistema, architettura) → artefatti accettati, dal preferito in giù.
PLATFORM_ASSETS = {
    ("Darwin", "arm64"): (".app.tar.gz", "aarch64.dmg"),
    ("Windows", "amd64"): ("-setup.exe", ".msi"),
    ("Linux", "amd64"): (".AppImage",),
}

_MACHINE_ALIASES = {"aarch64": "arm64", "x86_64": "amd64", "amd64": "amd64",
                    "arm64": "arm64", "AMD64": "amd64"}
```

con `pick_asset` che normalizza `machine`, cerca i pattern in ordine e ritorna `None` se nessuno combacia; `latest_release` che legge il JSON e salta le release senza artefatti; `download_asset` che scarica in un file temporaneo dentro `dest_dir`, calcola lo `sha256`, e **cancella il temporaneo** se l'impronta non torna (`InstallError("impronta sha256 diversa da quella dichiarata: …")`); `install` che smista per sistema:

- Darwin: `tarfile.open(...).extractall(dest_dir)` (con controllo dei percorsi: nessun membro assoluto o con `..`), poi `xattr -dr com.apple.quarantine <app>` — la build non è notarizzata e senza questo Gatekeeper dice «danneggiata».
- Linux: copia l'AppImage in `dest_dir`, `chmod 0o755`.
- Windows: `runner.Popen([str(archive), "/S"])` (il setup NSIS di Tauri installa per utente); se dopo l'attesa `_find_emstudio_executable()` non trova niente, rilancia il setup senza `/S` perché l'utente completi a mano.

- [ ] **Step 4: Run test to verify it passes**

Run: come allo Step 2.
Expected: PASS.

- [ ] **Step 5: `em_export` trova anche l'installazione nostra**

Test in `tests/sync/test_em_export.py`:

```python
def test_the_executable_is_found_in_our_own_tools_folder(tmp_path, monkeypatch):
    """Quello che installiamo noi deve essere trovato come quello di sistema."""
    app = tmp_path / "tools" / "EMStudio" / "EMStudio.app"
    app.mkdir(parents=True)
    monkeypatch.setattr(em_studio_installer, "install_dir",
                        lambda: tmp_path / "tools" / "EMStudio")
    assert em_export._find_emstudio_executable() == app
```

e in `em_export._find_emstudio_executable`, prima dei percorsi di sistema, guarda in `em_studio_installer.install_dir()` (import locale, per non creare un ciclo).

- [ ] **Step 6: La voce di menu e l'offerta quando manca**

In `pyarchinitPlugin.py`:

```python
    def _run_emstudio_install(self):
        """Conferma informata → scarica → installa → apri."""
        from qgis.PyQt.QtWidgets import QMessageBox
        from .modules.s3dgraphy import em_studio_installer as inst
        try:
            release = inst.latest_release()
            asset = inst.pick_asset(release["assets"], None, None)
        except Exception as e:                      # noqa: BLE001
            QMessageBox.critical(self.iface.mainWindow(), "EMStudio",
                                 "Non riesco a leggere le release di "
                                 "EMStudio:\n%s" % e)
            return
        if asset is None:
            QMessageBox.information(
                self.iface.mainWindow(), "EMStudio",
                "La release %s non pubblica un pacchetto per questo "
                "sistema (%s %s).\nScarica a mano da:\n%s"
                % (release["tag"], platform.system(), platform.machine(),
                   release["html_url"]))
            return
        answer = QMessageBox.question(
            self.iface.mainWindow(), "Installare EMStudio?",
            "Versione: %s\nFile: %s (%.1f MB)\nDa: %s\nIn: %s\n\n"
            "EMStudio è un programma separato (GPL-3) del progetto "
            "Extended Matrix: pyArchInit lo scarica e lo avvia, non lo "
            "incorpora.\n\nProcedere?"
            % (release["tag"], asset["name"], asset["size"] / 1e6,
               asset["browser_download_url"], inst.install_dir()),
            QMessageBox.Yes | QMessageBox.No)
        if answer != QMessageBox.Yes:
            return
```

poi il download/installazione in un `QgsTask` (come la consegna alla stanza), con l'esito in un `QMessageBox` e, se è andata, l'offerta di aprire subito il file em.json appena esportato. La voce di menu si chiama «Installa EMStudio…» e va accanto a «Esporta em.json…»; il nome dell'azione (`"actionEmStudioInstall"`) entra nella tupla di `unload()`.

Quando `open_in_emstudio` non trova l'eseguibile, al posto del `False` muto l'export propone l'installazione.

- [ ] **Step 7: Run the whole suite**

Run: il comando canonico su `tests/sync`.
Expected: PASS a parte il rumore noto.

- [ ] **Step 8: Commit**

```bash
git add modules/s3dgraphy/em_studio_installer.py modules/s3dgraphy/em_export.py pyarchinitPlugin.py tests/sync/test_em_studio_installer.py tests/sync/test_em_export.py
git commit -m "feat(emstudio): installazione automatica dalle release ufficiali, per ogni piattaforma"
```

---

## Chiusura

- Suite intera con il comando canonico.
- Collaudo vivo: pannello aperto su QtWebKit contro il nodo locale; installazione di EMStudio in una cartella di prova (`PYARCHINIT_HOME` a una copia) per non toccare quella di Enzo.
- `tutorial-updater` (voce di menu nuova, visibile all'utente) poi `stratigraph-changelog`.
- Review indipendente dell'intero ramo prima del tag; correzioni dentro la stessa release.
- Release: bump `metadata.txt`, changelog bilingue, tag `tools-reach-5.13.36-alpha`, push ramo + tag, `gh release create --prerelease`, voce api-docs RTD.
