"""Export a site to em.json, the working format of the Extended Matrix.

GraphML stays only as the one-time import from yEd (spec 2026-10-07):
the matrix a user looks at lives in EMStudio, which opens em.json
natively. The graph is built by the library's own DB->graph path
(PyArchInitImporter + pyarchinit_us_mapping), named after the site,
and read back before being handed over: a file that does not read
back clean is not given to the user.

Pure Python: no Qt. The menu wiring lives in pyarchinitPlugin.
"""
from __future__ import annotations

import os
import re


class EmExportError(RuntimeError):
    """A reason the export could not be done, worded for the user."""


def emjson_available():
    """True when the installed s3dgraphy knows em.json (>= 1.6.0.dev40)."""
    try:
        from s3dgraphy.exporter import emjson_exporter  # noqa: F401
        return True
    except Exception:
        return False


def site_filename(site):
    """A filename the site name can travel in: word characters of any
    script, dash and dot survive; runs of anything else become one '_'."""
    name = re.sub(r"[^\w\-.]+", "_", str(site), flags=re.UNICODE).strip("_.")
    return (name or "sito") + ".em.json"


def _claim_path(path, site):
    """The path this site's file may use.

    Two different sites can sanitize to the same name ('Scavo 1' and
    'Scavo/1' are both Scavo_1.em.json) and the second export silently
    overwrote the first (deferred minor, final review 2026-10-07).
    Re-exporting the SAME site keeps overwriting its own file — that is
    the idempotent case — but a file that belongs to ANOTHER site stays:
    this site gets the same name with a short stable suffix of its raw
    name, so the second delivery lands on the same file too.
    """
    if not os.path.exists(path):
        return path
    try:
        import json
        with open(path, encoding="utf-8") as fh:
            payload = json.load(fh)
        owner = payload.get("active_graph_id") or next(
            iter(payload.get("graphs", {}) or {}), None)
    except Exception:
        owner = None
    if owner == str(site):
        return path
    import hashlib
    tag = hashlib.sha1(str(site).encode("utf-8")).hexdigest()[:8]
    base = path[:-len(".em.json")]
    return "%s_%s.em.json" % (base, tag)


def saggi_del_sito(connection_url, site) -> list:
    """I saggi di un sito, in ordine. Vuoto quando non ce ne sono.

    Serve alla scelta «automatico»: dividere in un grafo per saggio ha
    senso solo dove i saggi ci sono davvero. Sul database di esempio sono
    zero — tutte le 51 US hanno il campo vuoto — quindi l'automatico là si
    comporta come oggi.
    """
    from sqlalchemy import text

    try:
        from s3dgraphy.sync._db_handle import _resolve_db_handle
        handle = _resolve_db_handle(connection_url)
        with handle.engine.connect() as conn:
            righe = conn.execute(text(
                "SELECT DISTINCT saggio FROM us_table WHERE sito = :s"),
                {"s": site}).fetchall()
    except Exception:                               # noqa: BLE001
        return []
    return sorted({str(r[0]).strip() for r in righe
                   if r[0] is not None and str(r[0]).strip()})


def export_site(connection_url, site, out_dir, per_saggio=None):
    """Build the site's graph, write <out_dir>/<site>.em.json, read it
    back. Returns (path, n_nodes, n_edges, warnings).

    ``per_saggio`` decide la forma del file:

    * ``False`` — **un grafo solo** per tutto il sito, com'è sempre stato;
    * ``True`` — **un grafo per ogni saggio**, più uno per le unità che non
      ne hanno (`GraphProjector.populate_container`, dev45). Un rapporto fra
      unità di due saggi diversi non si perde: diventa un `link` con
      l'indirizzo «grafo → nodo»;
    * ``None`` — **automatico**: per saggio quando il sito ne ha più d'uno,
      altrimenti un grafo solo. È il valore di prima, quindi nessuna
      chiamata esistente cambia comportamento su un sito senza saggi.

    The graph travels through the plugin's GraphProjector — NOT the raw
    importer: the dev40 mapping has no `relations` yet (s3Dgraphy#26),
    so only the projector's passes give the file the stratigraphic
    edges the matrix lives on (C1, final review 2026-10-07). Every
    failure on the way is worded for the user as EmExportError.
    """
    if not emjson_available():
        raise EmExportError(
            "La libreria s3dgraphy installata non conosce em.json: "
            "aggiorna le dipendenze del plugin.")
    from s3dgraphy.exporter.emjson_exporter import export_emjson
    from s3dgraphy.importer.emjson_importer import import_emjson
    from s3dgraphy.nodes.stratigraphic_node import StratigraphicNode

    from .sync.graph_projector import GraphProjector

    saggi = saggi_del_sito(connection_url, site) if per_saggio is not False \
        else []
    dividere = bool(per_saggio) if per_saggio is not None else len(saggi) > 1
    if dividere and not saggi:
        # Chiesto a mano su un sito che non ha saggi: si dice invece di
        # scrivere un contenitore di un grafo solo facendo finta di niente.
        raise EmExportError(
            "Il sito %r non ha saggi: non c'è niente da dividere." % site)

    contenitore = None
    try:
        if dividere:
            contenitore = GraphProjector().populate_container(
                connection_url, site, groups=["saggio"])
            grafi = list((getattr(contenitore, "graphs", None) or {}).values())
            graph = grafi[0] if grafi else None
            if graph is None:
                raise EmExportError(
                    "Il sito %r non ha prodotto nessun grafo." % site)
        else:
            graph = GraphProjector().populate_graph(connection_url, sito=site)
    except EmExportError:
        raise
    except Exception as e:
        raise EmExportError(
            "Lettura del sito %r fallita: %s" % (site, e)) from e
    tutti = (list((getattr(contenitore, "graphs", None) or {}).values())
             if contenitore is not None else [graph])
    strat = [n for g in tutti for n in (getattr(g, "nodes", []) or [])
             if isinstance(n, StratigraphicNode)]
    if not strat:
        raise EmExportError(
            "Il sito %r non ha righe in us_table: niente da esportare." % site)
    if contenitore is None:
        graph.graph_id = str(site)
    warnings = [str(w) for g in tutti
                for w in (getattr(g, "warnings", None) or [])]


    try:
        os.makedirs(out_dir, exist_ok=True)
        path = os.path.join(out_dir, site_filename(site))
        path = _claim_path(path, site)
        if contenitore is not None:
            from s3dgraphy.container import save_container_file
            # `bump=False`: questa è una conversione, non un salvataggio del
            # lavoro, e far avanzare la revisione del progetto direbbe una
            # cosa che non è successa (parole della sua docstring).
            save_container_file(contenitore, path, bump=False)
        else:
            export_emjson(graph, path)
    except Exception as e:
        raise EmExportError(
            "Scrittura di %s fallita: %s" % (site_filename(site), e)) from e

    nodi = sum(len(g.nodes) for g in tutti)
    archi = sum(len(g.edges) for g in tutti)
    try:
        if contenitore is not None:
            from s3dgraphy.container import load_container_file
            riletto, read_warnings = load_container_file(path)
            riletti = list((getattr(riletto, "graphs", None) or {}).values())
            letti = (sum(len(g.nodes) for g in riletti),
                     sum(len(g.edges) for g in riletti))
        else:
            check, read_warnings = import_emjson(path)
            letti = (len(check.nodes), len(check.edges))
    except Exception as e:
        raise EmExportError(
            "Il file scritto non si rilegge: %s" % e) from e
    if letti != (nodi, archi):
        raise EmExportError(
            "Il file scritto non rilegge uguale (%d/%d nodi, %d/%d archi)."
            % (letti[0], nodi, letti[1], archi))
    warnings.extend(str(w) for w in read_warnings)
    return path, nodi, archi, warnings


def _our_installation():
    """What «Installa EMStudio…» put in the plugin's data folder, or None."""
    try:
        from .em_studio_installer import installed_executable
        return installed_executable()
    except Exception:                               # noqa: BLE001
        return None


def _find_emstudio_executable():
    """The EMStudio executable, or None.

    Our own installation first — otherwise the user installs it from the
    menu and the plugin keeps saying it is not there — then PATH
    (`shutil.which`), then the places the installers use.
    """
    import shutil as _shutil

    ours = _our_installation()
    if ours is not None:
        return ours

    for name in ("EMStudio", "emstudio", "em-studio", "EMStudio.exe"):
        exe = _shutil.which(name)
        if exe:
            return exe
    candidates = []
    local = os.environ.get("LOCALAPPDATA")
    if local:
        candidates.append(os.path.join(
            local, "Programs", "EMStudio", "EMStudio.exe"))
    for pf in (os.environ.get("PROGRAMFILES"),
               os.environ.get("PROGRAMFILES(X86)")):
        if pf:
            candidates.append(os.path.join(pf, "EMStudio", "EMStudio.exe"))
    candidates += [
        "/opt/EMStudio/emstudio",
        os.path.expanduser("~/.local/bin/emstudio"),
        os.path.expanduser("~/Applications/EMStudio.AppImage"),
    ]
    # macOS: l'elenco non lo contemplava, e dentro il bundle l'eseguibile
    # si chiama `emstudio-desktop`, quindi nemmeno `which` lo trovava — con
    # EMStudio in /Applications questa funzione rispondeva **None**.
    #
    # Su macOS non cambia niente di quello che l'utente vede: lì
    # `open_in_emstudio` non la interroga, perché `open -a EMStudio`
    # risolve per nome tramite LaunchServices. Ma una funzione che si
    # chiama «trova l'eseguibile» e dice di no mentre l'applicazione c'è
    # è una trappola per il primo che la userà come «c'è?».
    for base in ("/Applications/EMStudio.app",
                 os.path.expanduser("~/Applications/EMStudio.app")):
        for interno in ("emstudio-desktop", "EMStudio"):
            candidates.append(os.path.join(base, "Contents", "MacOS", interno))
    for c in candidates:
        if os.path.isfile(c):
            return c
    return None


def open_in_emstudio(path, runner=None):
    """Hand the file to EMStudio; True only when EMStudio itself opened,
    False — never an exception — otherwise (the caller then points at
    the EMStudio releases page).

    Deferred-minor fix (final review 2026-10-07): on Windows/Linux the
    old `os.startfile`/`xdg-open` followed the .json association — an
    editor opened, the opener said True, and the download hint never
    showed. Now the file goes to a FOUND EMStudio executable or the
    opener says False.
    """
    import platform
    import subprocess
    run = runner or subprocess.run
    system = platform.system()
    try:
        if system == "Darwin":
            # Un'applicazione dentro la nostra cartella dati può non
            # essere registrata in LaunchServices: per nome non si
            # troverebbe, per percorso sì.
            ours = _our_installation()
            target = str(ours) if ours is not None else "EMStudio"
            return run(["open", "-a", target, path],
                       capture_output=True).returncode == 0
        exe = _find_emstudio_executable()
        if not exe:
            return False
        subprocess.Popen([exe, path])
        return True
    except Exception:
        return False
