"""Il progetto EM per EMStudio: l'em.json dentro ``EM/`` con i file che cita
(17 ottobre 2026).

EMStudio cerca i file a partire dalla cartella dell'em.json, nell'albero
standard di un progetto EM che la libreria definisce (``s3dgraphy.project_tree``,
deciso da Emanuel il 4 ottobre 2026): ``EM/`` l'em.json, ``EM/DosCo`` i
documenti, ``EM/proxies`` un glb per unità, ``RB`` il rilievo, ``SB`` i
modelli dalle fonti, ``RM`` i modelli di rappresentazione. Il risolutore è
uno per tutti gli strumenti (``s3dgraphy.resources.locate``, EMStudio lo usa
dal suo ponte): un percorso relativo si prova contro quelle cartelle, un nome
nudo anche in ``EM/DosCo`` — da lì EMStudio inietta l'url dei documenti e
degli estrattori (TempluMare: «D.07.05.jpg»).

L'em.json che pyArchInit scrive in ``pyarchinit_EM_folder`` porta quei
percorsi ma non i file: aperto da lì, EMStudio non trova i proxy né i
documenti (Enzo, 17 ottobre 2026: «controlla anche che EMStudio voglia una
struttura definita per i media»). Qui si fa la cartella del progetto:
l'em.json di lavoro — con la narrativa preparata nel pannello — copiato in
``EM/``, e accanto una copia di ogni file citato che il database conosce (i
media importati con l'em.json; se l'originale non si raggiunge, la copia
nella cartella delle ridotte quando è lo stesso file), al percorso che il
risolutore cerca. Poi il risolutore stesso dice quanti ne trova.

Un file che nel progetto c'è già ed è diverso non si sovrascrive (può essere
lavoro fatto in EMStudio): si dice. L'em.json di prima, se diverso, resta
accanto come ``.bak``. Quello che il database non conosce (il rilievo in
``RB/``, i ``.blend``: non sono media) si dice per cartella, da copiare a
mano dal progetto originale.
"""
from __future__ import annotations

import filecmp
import hashlib
import json
import os
import re
import shutil
from collections import Counter
from dataclasses import dataclass, field
from typing import Callable, Dict, Iterable, List, Optional, Tuple

#: le cartelle dell'albero standard (``s3dgraphy.project_tree.STANDARD_DIRS``)
_ALBERO = ("EM", "EM/DosCo", "EM/proxies", "RB", "SB", "RM")

#: i nodi i cui file il risolutore della libreria conta (``entries_of``)
_RISORSE = ("resource", "resource_file")


@dataclass
class ProjectResult:
    path: str = ""
    copied: List[str] = field(default_factory=list)
    unchanged: List[str] = field(default_factory=list)
    kept: List[str] = field(default_factory=list)
    missing: List[str] = field(default_factory=list)
    outside: List[str] = field(default_factory=list)
    mismatched: List[str] = field(default_factory=list)
    bytes: int = 0
    backup: str = ""
    found: int = 0
    resources: int = 0
    warnings: List[str] = field(default_factory=list)

    def summary(self) -> str:
        righe = ["em.json: %s" % self.path,
                 "%d file copiati (%.1f MB), %d già nel progetto" % (
                     len(self.copied), self.bytes / 1e6, len(self.unchanged))]
        if self.resources:
            righe.append("EMStudio trova dal progetto %d delle %d risorse dell'em.json"
                         % (self.found, self.resources))
        if self.kept:
            righe.append("%d file nel progetto diversi da quelli del database, lasciati come "
                         "sono (per sostituirli, cancellali e riesporta): %s"
                         % (len(self.kept), _esempi(self.kept)))
        if self.mismatched:
            righe.append("%d file copiati che non hanno lo sha256 scritto nell'em.json: %s"
                         % (len(self.mismatched), _esempi(self.mismatched)))
        if self.missing:
            per_cartella = Counter(_cartella(p) for p in self.missing)
            righe.append("%d file citati che il database non ha, da copiare a mano dal "
                         "progetto originale: %s" % (len(self.missing), ", ".join(
                             "%s/ %d" % (c, n) for c, n in per_cartella.most_common())))
        if self.outside:
            righe.append("%d percorsi fuori dalla cartella del progetto, lasciati com'erano"
                         % len(self.outside))
        if self.backup:
            righe.append("l'em.json di prima: %s" % self.backup)
        return "\n".join(righe)


def _esempi(voci: List[str], quanti: int = 4) -> str:
    return ", ".join(voci[:quanti]) + (" …" if len(voci) > quanti else "")


def _cartella(percorso: str) -> str:
    """La cartella dell'albero a cui il file appartiene: ``RB``, ``SB``…, e
    per quelli dentro ``EM`` la sua sottocartella (``EM/DosCo``)."""
    parti = percorso.replace("\\", "/").split("/")
    if parti[0] == "EM" and len(parti) > 2:
        return "/".join(parti[:2])
    return parti[0] if len(parti) > 1 else "."


def _locale(url: str) -> bool:
    if not url or "://" in url:
        return False
    return not (url.startswith(("/", "\\")) or re.match(r"^[A-Za-z]:[\\/]", url))


def _blend(url: str) -> str:
    """Il ``.blend`` di un datablock (``blend://<file>#<Tipo>/<nome>``): il
    risolutore cerca quel file."""
    try:
        from s3dgraphy.resources.resolver import parse_blend_locator
        trovato = parse_blend_locator(url)
    except ImportError:                                      # pragma: no cover
        trovato = None
    return trovato[0] if trovato else ""


def _grafi(doc: dict) -> Iterable[dict]:
    grafi = doc.get("graphs") or {}
    return [g or {} for g in (grafi.values() if isinstance(grafi, dict) else grafi)]


def _url_del_nodo(nodo: dict) -> List[str]:
    dati = nodo.get("data") or {}
    out = [str(dati.get("url") or "").strip()]
    out += [str(a.get("locator") or "").strip()
            for a in dati.get("addresses") or [] if isinstance(a, dict)]
    return [_blend(u) if u.lower().startswith("blend://") else u for u in out if u]


def project_locators(doc: dict) -> List[str]:
    """I percorsi relativi dei file che l'em.json cita — l'``url`` dei nodi,
    gli indirizzi alternativi (``addresses``) e il ``.blend`` dei datablock —,
    una volta sola, nell'ordine del file. Gli indirizzi web e del cloud e i
    percorsi assoluti non sono file del progetto."""
    out: List[str] = []
    for g in _grafi(doc):
        for nodo in g.get("nodes") or []:
            for url in _url_del_nodo(nodo):
                if _locale(url) and url not in out:
                    out.append(url)
    return out


def project_path(locator: str) -> str:
    """Dove sta il file nel progetto, rispetto a ``EM/`` come lo intende
    l'em.json: il percorso com'è, o ``DosCo/<nome>`` per un nome nudo."""
    parti = [p for p in re.split(r"[\\/]+", str(locator)) if p and p != "."]
    if len(parti) == 1:
        parti = ["DosCo"] + parti
    return "/".join(parti)


def project_root_for(chosen: str, site: str) -> str:
    """La cartella del progetto per la cartella scelta: lei stessa se è
    vuota (i file nascosti non contano) o è già un progetto EM (ha ``EM/``,
    o è la ``EM/`` di un progetto); altrimenti una cartella nuova col nome
    del sito dentro di lei, perché l'albero non si sparga fra i file di
    un'altra cartella."""
    from .em_export import site_filename
    scelta = os.path.abspath(os.path.expanduser(str(chosen)))
    if os.path.basename(scelta) == "EM" and os.path.isdir(scelta):
        return os.path.dirname(scelta)
    if os.path.isdir(os.path.join(scelta, "EM")):
        return scelta
    try:
        visibili = [n for n in os.listdir(scelta) if not n.startswith(".")]
    except OSError:
        visibili = []
    if not visibili:
        return scelta
    return os.path.join(scelta, site_filename(site)[:-len(".em.json")])


def media_index(connection_url: str, resize_base: str = "") -> Dict[str, List[Tuple[str, bool]]]:
    """Dal nome del file (minuscolo) ai posti dove sta: l'originale
    registrato nel media e la sua copia nella cartella delle ridotte
    (``media_thumb_table.path_resize``), segnata come copia."""
    from sqlalchemy import create_engine, text
    indice: Dict[str, List[Tuple[str, bool]]] = {}
    engine = create_engine(connection_url)
    try:
        with engine.connect() as conn:
            try:
                righe = conn.execute(text(
                    "SELECT m.filename, m.filetype, m.filepath, t.path_resize FROM media_table m "
                    "LEFT JOIN media_thumb_table t ON t.id_media = m.id_media")).fetchall()
            except Exception:                                # noqa: BLE001
                righe = [tuple(r) + (None,) for r in conn.execute(text(
                    "SELECT filename, filetype, filepath FROM media_table")).fetchall()]
    except Exception:                                        # noqa: BLE001
        righe = []
    finally:
        engine.dispose()
    for nome, tipo, percorso, copia in righe:
        originale = str(percorso or "")
        chiave = os.path.basename(originale).lower() or ("%s.%s" % (nome, tipo)).lower()
        posti = indice.setdefault(chiave, [])
        if originale and (originale, False) not in posti:
            posti.append((originale, False))
        if resize_base and copia:
            posti.append((os.path.join(resize_base, str(copia)), True))
    return indice


def media_file_for(locator: str, index: Dict[str, List[Tuple[str, bool]]]) -> Optional[str]:
    """Il file da copiare per ``locator``. Prima gli originali: quello il
    cui percorso finisce come il locator (due file con lo stesso nome in
    cartelle diverse), altrimenti il primo che c'è. Se l'originale non si
    raggiunge (il disco del progetto staccato), la copia nella cartella
    delle ridotte, ma solo se è lo stesso tipo di file: un'immagine lì è
    ridotta in PNG, non è più il file citato."""
    posti = index.get(os.path.basename(locator).lower(), [])
    originali = [p for p, copia in posti if not copia and os.path.isfile(p)]
    coda = "/".join(x for x in re.split(r"[\\/]+", locator) if x not in ("", ".", ".."))
    for p in originali:
        if p.replace("\\", "/").endswith("/" + coda):
            return p
    if originali:
        return originali[0]
    estensione = os.path.splitext(locator)[1].lower()
    for p, copia in posti:
        if copia and os.path.splitext(p)[1].lower() == estensione and os.path.isfile(p):
            return p
    return None


def _uguali(a: str, b: str) -> bool:
    try:
        if os.path.samefile(a, b):
            return True
        if os.path.getsize(a) != os.path.getsize(b):
            return False
        if abs(os.path.getmtime(a) - os.path.getmtime(b)) < 2:
            return True                                      # copy2 tiene la data
        return filecmp.cmp(a, b, shallow=False)
    except OSError:
        return False


def _sha256(percorso: str) -> str:
    h = hashlib.sha256()
    with open(percorso, "rb") as fh:
        for pezzo in iter(lambda: fh.read(1 << 20), b""):
            h.update(pezzo)
    return h.hexdigest()


def _impronte(doc: dict) -> Dict[str, str]:
    """Dal locator allo sha256 che l'em.json gli scrive (``data.checksum``)."""
    out: Dict[str, str] = {}
    for g in _grafi(doc):
        for nodo in g.get("nodes") or []:
            impronta = str((nodo.get("data") or {}).get("checksum") or "").strip().lower()
            if impronta.startswith("sha256:"):
                impronta = impronta[7:]
            if re.fullmatch(r"[0-9a-f]{64}", impronta):
                for url in _url_del_nodo(nodo):
                    out.setdefault(url, impronta)
    return out


def _trovati(doc: dict, radice: str) -> Tuple[int, int]:
    """Quante risorse dell'em.json con un file del progetto il risolutore
    della libreria trova sul disco partendo da ``radice``, e quante sono."""
    try:
        from s3dgraphy.resources.locate import resolve
    except ImportError:                                      # pragma: no cover
        return 0, 0
    trovati = tutte = 0
    for g in _grafi(doc):
        for nodo in g.get("nodes") or []:
            if nodo.get("node_type") not in _RISORSE:
                continue
            if not any(_locale(u) for u in _url_del_nodo(nodo)):
                continue
            dati = nodo.get("data") or {}
            voce = {"id": nodo.get("id"), "locator": str(dati.get("url") or ""),
                    "addresses": [str(a.get("locator")) for a in dati.get("addresses") or []
                                  if isinstance(a, dict) and a.get("locator")]}
            tutte += 1
            if resolve(voce, project_root=radice)["state"] in ("on_disk", "both"):
                trovati += 1
    return trovati, tutte


def export_project(connection_url: str, site: str, dest_dir: str, *,
                   work_dir: Optional[str] = None, resize_base: str = "",
                   progress: Optional[Callable[[int, int, str], None]] = None) -> ProjectResult:
    """Esporta il sito come «Esporta sito in em.json…» (nella cartella di
    lavoro, così la narrativa resta), fa l'albero standard in ``dest_dir``,
    copia l'em.json in ``dest_dir/EM/`` e accanto i file che cita."""
    from . import em_export
    if work_dir is None:
        from ..utility.pyarchinit_home import pyarchinit_home
        work_dir = os.path.join(str(pyarchinit_home()), "pyarchinit_EM_folder")
    esito = ProjectResult()
    percorso, _nodi, _archi, avvisi = em_export.export_site(connection_url, site, work_dir,
                                                             per_saggio=False)
    esito.warnings = [str(a) for a in avvisi]
    radice = os.path.abspath(dest_dir)
    for cartella in _ALBERO:
        os.makedirs(os.path.join(radice, *cartella.split("/")), exist_ok=True)
    cartella_em = os.path.join(radice, "EM")
    esito.path = os.path.join(cartella_em, os.path.basename(percorso))
    if os.path.isfile(esito.path) and not _uguali(percorso, esito.path):
        esito.backup = esito.path + ".bak"
        shutil.copy2(esito.path, esito.backup)
    shutil.copy2(percorso, esito.path)
    with open(esito.path, encoding="utf-8") as fh:
        documento = json.load(fh)
    impronte = _impronte(documento)
    indice = media_index(connection_url, resize_base)
    locators = project_locators(documento)
    visti = set()
    for i, locator in enumerate(locators):
        if progress is not None:
            progress(i, len(locators), locator)
        bersaglio = os.path.abspath(os.path.join(cartella_em, *project_path(locator).split("/")))
        if bersaglio == radice or not bersaglio.startswith(radice + os.sep):
            esito.outside.append(locator)
            continue
        if bersaglio in visti:
            continue                    # «D.05.pdf» e «DosCo/D.05.pdf»: lo stesso file
        visti.add(bersaglio)
        voce = os.path.relpath(bersaglio, radice).replace(os.sep, "/")
        sorgente = media_file_for(locator, indice)
        if sorgente is None:
            (esito.unchanged if os.path.isfile(bersaglio) else esito.missing).append(voce)
            continue
        if os.path.isfile(bersaglio):
            (esito.unchanged if _uguali(sorgente, bersaglio) else esito.kept).append(voce)
            continue
        os.makedirs(os.path.dirname(bersaglio), exist_ok=True)
        shutil.copy2(sorgente, bersaglio)
        esito.copied.append(voce)
        esito.bytes += os.path.getsize(bersaglio)
        atteso = impronte.get(locator)
        if atteso and _sha256(bersaglio) != atteso:
            esito.mismatched.append(voce)
    if progress is not None:
        progress(len(locators), len(locators), "")
    esito.found, esito.resources = _trovati(documento, radice)
    return esito
