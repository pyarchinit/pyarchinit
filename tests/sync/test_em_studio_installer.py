"""EMStudio si installa da sé, su ogni piattaforma (2026-10-08).

Chiesto da Enzo: «se EMStudio non è installato facciamo in modo che possa
essere installato in automatico (su tutte le piattaforme)».

Il plugin non contiene e non collega codice EMStudio (GPL-3): scarica il
binario ufficiale quando l'utente lo chiede e lo avvia come processo
separato, come già fa l'apertura del file em.json.

Nessun test tocca la rete: l'HTTP è iniettato.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from modules.s3dgraphy.em_studio_installer import (  # noqa: E402
    InstallError,
    RELEASES_URL,
    download_asset,
    install,
    install_dir,
    latest_release,
    pick_asset,
)

# Gli artefatti veri della v1.6.0-dev.26 (nomi e dimensioni letti
# dall'API il 2026-10-08).
ASSETS = [
    {"name": "EMStudio-1.6.0-1.x86_64.rpm", "size": 62105656,
     "digest": "sha256:0ad2", "browser_download_url": "https://x/rpm"},
    {"name": "EMStudio_1.6.0_aarch64.dmg", "size": 37735827,
     "digest": "sha256:3571", "browser_download_url": "https://x/dmg"},
    {"name": "EMStudio_1.6.0_amd64.AppImage", "size": 140102136,
     "digest": "sha256:17f1", "browser_download_url": "https://x/appimage"},
    {"name": "EMStudio_1.6.0_amd64.deb", "size": 62104684,
     "digest": "sha256:ae6f", "browser_download_url": "https://x/deb"},
    {"name": "EMStudio_1.6.0_x64-setup.exe", "size": 39688057,
     "digest": "sha256:ea2f", "browser_download_url": "https://x/exe"},
    {"name": "EMStudio_1.6.0_x64_en-US.msi", "size": 40955904,
     "digest": "sha256:bec5", "browser_download_url": "https://x/msi"},
    {"name": "EMStudio_aarch64.app.tar.gz", "size": 37458736,
     "digest": "sha256:bf3f", "browser_download_url": "https://x/tgz"},
]


def test_each_platform_gets_its_own_artefact():
    """Mac ARM preferisce il .app.tar.gz (si estrae senza montare un
    disco), Windows il setup, Linux l'AppImage (non chiede root)."""
    assert pick_asset(ASSETS, "Darwin", "arm64")["name"].endswith(
        ".app.tar.gz")
    assert pick_asset(ASSETS, "Windows", "AMD64")["name"].endswith(
        "-setup.exe")
    assert pick_asset(ASSETS, "Linux", "x86_64")["name"].endswith(".AppImage")


def test_mac_intel_says_there_is_no_package_instead_of_crashing():
    """La release di oggi non pubblica niente per Mac Intel: si risponde
    None, e chi chiama lo dice a parole."""
    assert pick_asset(ASSETS, "Darwin", "x86_64") is None


def test_an_unknown_platform_is_not_a_guess():
    assert pick_asset(ASSETS, "FreeBSD", "amd64") is None
    assert pick_asset([], "Darwin", "arm64") is None


def test_the_release_list_is_read_because_latest_is_a_prerelease():
    """EMStudio pubblica SOLO pre-release: /releases/latest risponde 404."""
    assert "/releases?" in RELEASES_URL
    assert "/releases/latest" not in RELEASES_URL


def test_the_newest_release_with_artefacts_wins():
    payload = json.dumps([
        {"tag_name": "v1.6.0-dev.27", "assets": [],
         "html_url": "https://h/27"},
        {"tag_name": "v1.6.0-dev.26", "assets": ASSETS,
         "html_url": "https://h/26"},
    ]).encode("utf-8")
    release = latest_release(http=lambda url, timeout=0: payload)
    assert release["tag"] == "v1.6.0-dev.26"
    assert release["html_url"] == "https://h/26"
    assert len(release["assets"]) == len(ASSETS)


def test_a_release_list_without_artefacts_is_a_sentence():
    with pytest.raises(InstallError, match="nessun pacchetto"):
        latest_release(http=lambda url, timeout=0: b"[]")


def test_a_download_whose_digest_does_not_match_is_thrown_away(tmp_path):
    asset = {"name": "EMStudio_aarch64.app.tar.gz", "size": 4,
             "digest": "sha256:" + "0" * 64,
             "browser_download_url": "https://x/tgz"}
    with pytest.raises(InstallError, match="impronta"):
        download_asset(asset, tmp_path, http=lambda url, timeout=0: b"ciao")
    assert list(tmp_path.iterdir()) == [], "niente file a metà"


def test_a_good_download_keeps_its_name(tmp_path):
    body = b"contenuto finto"
    asset = {"name": "EMStudio_aarch64.app.tar.gz", "size": len(body),
             "digest": "sha256:" + hashlib.sha256(body).hexdigest(),
             "browser_download_url": "https://x/tgz"}
    got = download_asset(asset, tmp_path, http=lambda url, timeout=0: body)
    assert got.name == "EMStudio_aarch64.app.tar.gz"
    assert got.read_bytes() == body


def test_an_asset_without_a_digest_is_still_accepted(tmp_path):
    """Una release più vecchia può non dichiarare l'impronta: si scarica
    lo stesso, perché il rifiuto bloccherebbe l'installazione."""
    body = b"x"
    asset = {"name": "EMStudio_amd64.AppImage", "size": 1,
             "browser_download_url": "https://x/a"}
    assert download_asset(asset, tmp_path,
                          http=lambda url, timeout=0: body).exists()


def test_a_tar_that_escapes_its_folder_is_refused(tmp_path):
    """Un archivio scaricato è dato altrui: nessun membro può scrivere
    fuori dalla cartella di destinazione."""
    import tarfile

    cattivo = tmp_path / "EMStudio_aarch64.app.tar.gz"
    payload = tmp_path / "payload"
    payload.write_text("x", encoding="utf-8")
    with tarfile.open(cattivo, "w:gz") as tar:
        tar.add(payload, arcname="../fuori.txt")
    with pytest.raises(InstallError, match="fuori"):
        install(cattivo, tmp_path / "dest", system="Darwin",
                runner=_RunnerFinto())


def test_an_appimage_is_made_runnable(tmp_path):
    import os
    import stat

    appimage = tmp_path / "EMStudio_amd64.AppImage"
    appimage.write_bytes(b"ELF finto")
    dest = tmp_path / "dest"
    got = install(appimage, dest, system="Linux", runner=_RunnerFinto())
    assert got.exists() and got.parent == dest
    assert os.stat(got).st_mode & stat.S_IXUSR


def test_the_windows_setup_is_run_silently(tmp_path):
    setup = tmp_path / "EMStudio_1.6.0_x64-setup.exe"
    setup.write_bytes(b"MZ")
    runner = _RunnerFinto()
    install(setup, tmp_path / "dest", system="Windows", runner=runner)
    assert runner.comandi and runner.comandi[0][0] == str(setup)
    assert "/S" in runner.comandi[0]


def test_the_install_folder_lives_in_the_pyarchinit_home(tmp_path,
                                                         monkeypatch):
    monkeypatch.setenv("PYARCHINIT_HOME", str(tmp_path))
    folder = install_dir()
    assert folder.parts[-2:] == ("tools", "EMStudio")
    assert str(tmp_path) in str(folder)


class _RunnerFinto:
    def __init__(self):
        self.comandi = []

    def Popen(self, cmd, **kwargs):          # noqa: N802 (API subprocess)
        self.comandi.append(list(cmd))
        return self

    def wait(self, timeout=None):
        return 0

    def run(self, cmd, **kwargs):
        self.comandi.append(list(cmd))
        return self
