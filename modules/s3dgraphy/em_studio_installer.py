"""Scarica e installa EMStudio, il visore dell'Extended Matrix.

Il plugin non contiene e non collega codice EMStudio (GPL-3): scarica il
binario ufficiale dalle release GitHub **quando l'utente lo chiede** e lo
esegue come processo separato, esattamente come già fa
``em_export.open_in_emstudio``. Il confine resta quello di oggi.

Due cose da ricordare, misurate il 2026-10-08:

* EMStudio pubblica **solo pre-release**, quindi ``/releases/latest``
  risponde 404: si legge la lista e si prende la prima release che abbia
  artefatti;
* l'API dichiara per ogni artefatto il suo ``digest`` sha256, e qui si
  verifica. La build non è notarizzata: su macOS, senza togliere la
  quarantena, Gatekeeper dice «danneggiata».

La release ``v1.6.0-dev.26`` non pubblica nulla per Mac Intel: in quel
caso ``pick_asset`` risponde ``None`` e chi chiama lo dice a parole.
"""
from __future__ import annotations

import hashlib
import json
import os
import platform
import shutil
import stat
import subprocess
import tarfile
from pathlib import Path

RELEASES_URL = ("https://api.github.com/repos/ExtendedMatrix/EMStudio"
                "/releases?per_page=5")

#: Quanto aspettare la rete, in secondi: l'API è svelta, il file no.
API_TIMEOUT = 15
DOWNLOAD_TIMEOUT = 600

#: (sistema, architettura) → code degli artefatti accettati, dal
#: preferito in giù. Su macOS il ``.app.tar.gz`` batte il ``.dmg``:
#: si estrae senza montare un disco. Su Linux l'AppImage batte .deb/.rpm:
#: non chiede i permessi di amministratore.
PLATFORM_ASSETS = {
    ("darwin", "arm64"): (".app.tar.gz", "aarch64.dmg"),
    ("windows", "amd64"): ("-setup.exe", ".msi"),
    ("linux", "amd64"): (".appimage",),
    ("linux", "arm64"): (".appimage",),
}

_MACHINE_ALIASES = {
    "aarch64": "arm64", "arm64": "arm64",
    "x86_64": "amd64", "amd64": "amd64", "x64": "amd64", "i386": "amd64",
}


class InstallError(Exception):
    """Un guasto da raccontare all'utente in una frase."""


def install_dir() -> Path:
    """La cartella nostra dove mettere EMStudio."""
    from modules.utility.pyarchinit_home import pyarchinit_home
    return Path(pyarchinit_home()) / "tools" / "EMStudio"


def _http(url, timeout=API_TIMEOUT) -> bytes:
    import urllib.request
    request = urllib.request.Request(
        url, headers={"Accept": "application/vnd.github+json",
                      "User-Agent": "pyArchInit"})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return response.read()


def _normalise(system, machine):
    system = str(system or platform.system()).strip().lower()
    machine = str(machine or platform.machine()).strip().lower()
    return system, _MACHINE_ALIASES.get(machine, machine)


def pick_asset(assets, system=None, machine=None):
    """L'artefatto giusto per questo computer, o None se non c'è.

    ``None`` non è un errore: la release può semplicemente non
    pubblicare nulla per quella piattaforma (oggi è il caso di Mac
    Intel). Chi chiama lo dice all'utente.
    """
    wanted = PLATFORM_ASSETS.get(_normalise(system, machine))
    if not wanted:
        return None
    for code in wanted:
        for asset in assets or ():
            if str(asset.get("name", "")).lower().endswith(code):
                return asset
    return None


def latest_release(http=_http) -> dict:
    """La release più recente che abbia artefatti.

    ``/releases/latest`` non serve: EMStudio pubblica solo pre-release e
    quell'indirizzo risponde 404.
    """
    try:
        payload = json.loads(http(RELEASES_URL, timeout=API_TIMEOUT))
    except InstallError:
        raise
    except Exception as e:                          # noqa: BLE001
        raise InstallError(
            "Non riesco a leggere le release di EMStudio: %s" % e) from e
    for release in payload or ():
        if release.get("assets"):
            return {"tag": release.get("tag_name", "?"),
                    "assets": release["assets"],
                    "html_url": release.get("html_url", "")}
    raise InstallError(
        "Le release di EMStudio non pubblicano nessun pacchetto scaricabile.")


def _expected_digest(asset):
    digest = str(asset.get("digest") or "")
    return digest.split(":", 1)[1].strip().lower() if ":" in digest else ""


def download_asset(asset, dest_dir, http=_http) -> Path:
    """Scarica l'artefatto in ``dest_dir``, verificando lo sha256.

    Se l'impronta non torna il file viene cancellato e non si installa
    niente. Una release che non dichiara l'impronta si accetta lo stesso:
    rifiutarla bloccherebbe l'installazione senza rendere nessuno più
    sicuro.
    """
    dest_dir = Path(dest_dir)
    dest_dir.mkdir(parents=True, exist_ok=True)
    url = asset.get("browser_download_url")
    if not url:
        raise InstallError("L'artefatto non dichiara un indirizzo da cui "
                           "scaricarlo.")
    try:
        body = http(url, timeout=DOWNLOAD_TIMEOUT)
    except Exception as e:                          # noqa: BLE001
        raise InstallError("Scaricamento fallito: %s" % e) from e

    expected = _expected_digest(asset)
    if expected:
        got = hashlib.sha256(body).hexdigest()
        if got != expected:
            raise InstallError(
                "Il file scaricato ha un'impronta sha256 diversa da quella "
                "dichiarata (%s invece di %s): non lo installo."
                % (got[:12], expected[:12]))

    target = dest_dir / str(asset.get("name") or "EMStudio")
    target.write_bytes(body)
    return target


def _safe_members(tar, dest_dir: Path):
    """I membri dell'archivio che restano dentro ``dest_dir``."""
    root = dest_dir.resolve()
    for member in tar.getmembers():
        destination = (root / member.name).resolve()
        if root != destination and root not in destination.parents:
            raise InstallError(
                "L'archivio scrive fuori dalla cartella di destinazione "
                "(«%s»): non lo apro." % member.name)
        yield member


def install(archive, dest_dir, system=None, runner=subprocess) -> Path:
    """Installa l'artefatto scaricato e ritorna quello che si avvia."""
    archive = Path(archive)
    dest_dir = Path(dest_dir)
    dest_dir.mkdir(parents=True, exist_ok=True)
    system, _machine = _normalise(system, None)
    name = archive.name.lower()

    if name.endswith(".tar.gz"):
        with tarfile.open(archive, "r:gz") as tar:
            tar.extractall(dest_dir, members=list(_safe_members(tar, dest_dir)))
        app = next((p for p in dest_dir.glob("*.app")), None)
        if app is None:
            raise InstallError(
                "Nell'archivio non c'è nessuna applicazione EMStudio.")
        _strip_quarantine(app, runner)
        return app

    if name.endswith(".appimage"):
        target = dest_dir / archive.name
        if archive.resolve() != target.resolve():
            shutil.move(str(archive), str(target))
        target.chmod(target.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP
                     | stat.S_IXOTH)
        return target

    if name.endswith((".exe", ".msi")):
        # Il setup NSIS di Tauri installa per utente: /S lo fa in
        # silenzio. Se non arriva in fondo, chi chiama lo rilancia senza
        # /S perché l'utente completi a mano.
        command = ([str(archive), "/S"] if name.endswith(".exe")
                   else ["msiexec", "/i", str(archive), "/qn"])
        process = runner.Popen(command)
        try:
            process.wait(timeout=600)
        except Exception:                           # noqa: BLE001
            pass
        return archive

    if name.endswith(".dmg"):
        raise InstallError(
            "Il pacchetto .dmg va aperto a mano: questa release non "
            "pubblica un archivio estraibile per questo Mac.")

    raise InstallError("Non so installare «%s»." % archive.name)


def _strip_quarantine(app_path, runner=subprocess):
    """Toglie la quarantena: la build non è notarizzata e senza questo
    macOS dice che l'applicazione è «danneggiata»."""
    try:
        runner.run(["xattr", "-dr", "com.apple.quarantine", str(app_path)],
                   check=False)
    except Exception:                               # noqa: BLE001
        pass                                        # al peggio lo dice macOS


def installed_executable():
    """Quello che abbiamo installato noi, se c'è."""
    folder = install_dir()
    if not folder.exists():
        return None
    for pattern in ("*.app", "*.AppImage", "EMStudio.exe"):
        found = next((p for p in folder.glob(pattern)), None)
        if found is not None:
            return found
    return None


def install_latest(http=_http, runner=subprocess, system=None, machine=None):
    """Tutto il giro: leggi, scegli, scarica, installa. Ritorna il percorso."""
    release = latest_release(http=http)
    asset = pick_asset(release["assets"], system, machine)
    if asset is None:
        raise InstallError(
            "La release %s non pubblica un pacchetto per questo sistema "
            "(%s %s). Si può scaricare a mano da %s"
            % (release["tag"], platform.system(), platform.machine(),
               release.get("html_url") or "github.com/ExtendedMatrix/EMStudio"))
    folder = install_dir()
    folder.mkdir(parents=True, exist_ok=True)
    archive = download_asset(asset, folder, http=http)
    try:
        return install(archive, folder, system=system, runner=runner)
    finally:
        if archive.exists() and archive.suffix.lower() in (".gz",):
            try:
                os.remove(archive)
            except OSError:
                pass
