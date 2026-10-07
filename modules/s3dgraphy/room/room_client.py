"""Portare le operazioni alla stanza. Niente altro.

Porting dichiarato di ``pyarchinit_mini/web_interface/room_client.py`` con le
sue quattro regole: (1) configurazione per ambiente, assente = spento; (2)
niente identità, niente consegna NÉ rete — qui l'identità la decide il
preflight ``/v1/health``: un nodo ``dev-no-auth`` non la chiede, uno con auth
vera esige ``STRATIGRAPH_TOKEN`` PRIMA di qualsiasi POST; (3) POST sincroni
senza coda né retry — una differenza dal mini, dichiarata: i NOSTRI siti
superano le 1000 op, quindi il lotto si spezza in pagine ≤1000 consegnate in
sequenza, fail-fast alla prima rete caduta, mai un retry; (4) ``author`` e
``ts`` li scrive il server.

E UN RIFIUTO DELLA STANZA NON È UN ERRORE: ``refused`` dentro un 200 è la
risposta normale alla seconda consegna (i nodi FONDONO, gli archi tornano
``idempotent`` — misurato sul nodo locale il 2026-10-07). Mai ``graph_id``
nel payload: una stanza, un grafo vivo.
"""
from __future__ import annotations

import json
import logging
import os
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple

log = logging.getLogger(__name__)

SERVER_URL_VARIABLE = "STRATIGRAPH_SERVER_URL"
ROOM_ID_VARIABLE = "STRATIGRAPH_ROOM_ID"
TOKEN_VARIABLE = "STRATIGRAPH_TOKEN"          # SOLO env: un token non si salva
QSETTINGS_URL = "pyarchinit/stratigraph/server_url"
QSETTINGS_ROOM = "pyarchinit/stratigraph/room_id"
BATCH_MAX = 1000
TIMEOUT = 30.0        # una pagina di ops sotto il lock della stanza
PROBE_TIMEOUT = 5.0   # una sonda (health, porta UI) non tiene in ostaggio


def _do_http(method, url, payload, token, timeout):
    body = json.dumps(payload).encode("utf-8") if payload is not None else None
    headers = {"Content-Type": "application/json",
               "Accept": "application/json"}
    if token:
        headers["Authorization"] = "Bearer %s" % token
    req = urllib.request.Request(url, data=body, method=method,
                                 headers=headers)
    with urllib.request.urlopen(req, timeout=timeout) as answer:
        raw = answer.read().decode("utf-8", "replace")
        try:
            return answer.status, json.loads(raw or "{}")
        except Exception:
            # una porta della UI risponde HTML: lo status basta
            return answer.status, {}


def _urllib_http(method, url, payload, token):
    return _do_http(method, url, payload, token, TIMEOUT)


def _probe_http(method, url, payload, token):
    return _do_http(method, url, payload, token, PROBE_TIMEOUT)


Http = Callable[[str, str, Optional[Dict[str, Any]], str],
                Tuple[int, Dict[str, Any]]]


def token_in_the_clear(settings) -> bool:
    """True quando il token viaggerebbe in chiaro: http:// verso un nodo
    che non è questa macchina (minor 12, review 2026-10-07)."""
    if not settings.token or not settings.server_url.startswith("http://"):
        return False
    import urllib.parse
    host = urllib.parse.urlsplit(settings.server_url).hostname or ""
    return host not in ("localhost", "127.0.0.1", "::1")


def _qsetting(key):
    try:
        from qgis.PyQt.QtCore import QSettings
        return str(QSettings().value(key, "") or "").strip()
    except Exception:
        return ""


class NodeSettings:
    """Dove sta il nodo e quale stanza. Env prima, QSettings poi; il token
    SOLO da env (pattern modules/storage/credentials.py)."""

    def __init__(self):
        self.server_url = (os.environ.get(SERVER_URL_VARIABLE, "").strip()
                           or _qsetting(QSETTINGS_URL)).rstrip("/")
        self.room_id = (os.environ.get(ROOM_ID_VARIABLE, "").strip()
                        or _qsetting(QSETTINGS_ROOM))
        self.token = os.environ.get(TOKEN_VARIABLE, "").strip()

    @property
    def enforcing(self):
        return bool(self.server_url and self.room_id)

    @property
    def ops_endpoint(self):
        import urllib.parse
        return "%s/v1/rooms/%s/ops" % (
            self.server_url, urllib.parse.quote(self.room_id, safe=""))


class RoomRefusal(RuntimeError):
    """Qualcosa che questo modulo non fa, in una frase per una persona."""


@dataclass
class Outcome:
    sent: int = 0
    applied: int = 0
    refused: List[Dict[str, Any]] = field(default_factory=list)
    skipped: List[str] = field(default_factory=list)
    counts: Dict[str, int] = field(default_factory=dict)
    room_id: str = ""
    batches: int = 0

    @property
    def idempotent(self):
        return sum(1 for r in self.refused
                   if r.get("reason") == "idempotent")

    @property
    def other_refusals(self):
        return [r for r in self.refused if r.get("reason") != "idempotent"]

    @property
    def a_repeat(self):
        return (self.sent > 0 and self.idempotent > 0
                and self.idempotent + self.applied == self.sent
                and not self.other_refusals)

    def summary(self):
        parts = ["%d applicate su %d" % (self.applied, self.sent)]
        if self.idempotent:
            parts.append("%d già presenti" % self.idempotent)
        if self.other_refusals:
            parts.append("%d rifiutate" % len(self.other_refusals))
        if self.skipped:
            parts.append("%d righe non tradotte" % len(self.skipped))
        return ", ".join(parts)


def preflight(server_url, http: Http = _probe_http):
    try:
        status, body = http("GET", server_url + "/v1/health", None, "")
    except Exception as exc:
        raise RoomRefusal(
            "Non ho potuto raggiungere il nodo (%s/v1/health): %s. "
            "Riprova quando il nodo risponde — niente coda."
            % (server_url, exc)) from exc
    if status != 200 or not body.get("ok"):
        raise RoomRefusal("Il nodo %s non sta bene (HTTP %d): consegna "
                          "rifiutata." % (server_url, status))
    return body


def _require_identity(settings, http: Http = _probe_http):
    """Regola 2, adattata: l'identità la esige il NODO, non noi. Un nodo
    dev-no-auth non la chiede; uno vero la chiede PRIMA di ogni POST.

    Dietro Caddy l'API vive su ``/em/v1/…`` (I3, review 2026-10-07): se la
    radice non risponde si prova ``/em``, e la base risolta RESTA sulle
    settings — così anche le ops vanno dalla porta giusta."""
    try:
        health = preflight(settings.server_url, http)
    except RoomRefusal as first:
        try:
            health = preflight(settings.server_url + "/em", http)
        except RoomRefusal:
            raise first from None
        settings.server_url = settings.server_url + "/em"
    if health.get("auth") != "dev-no-auth" and not settings.token:
        raise RoomRefusal(
            "Il nodo %s esige un'identità (%s) e %s non è impostata: "
            "senza un nome verificato non si scrive nel grafo di nessuno. "
            "Procurati un token dal nodo e mettilo in %s."
            % (settings.server_url, health.get("auth") or "auth",
               TOKEN_VARIABLE, TOKEN_VARIABLE))
    return health


def _deliver_ops(ops, settings, http: Http = _urllib_http):
    out = Outcome(sent=len(ops), room_id=settings.room_id)
    page_size = BATCH_MAX
    start = 0
    while start < len(ops):
        page = ops[start:start + page_size]
        try:
            status, answer = http("POST", settings.ops_endpoint,
                                  {"ops": page}, settings.token)
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", "replace")[:400]
            try:
                detail = json.loads(detail).get("detail") or detail
            except Exception:
                pass
            if exc.code == 413:
                # Il nodo accetta meno di BATCH_MAX (configurabile, e la
                # health non lo espone): la taglia sta nel detail. La
                # pagina respinta NON è stata applicata — ri-paginarla non
                # è ritentare un rifiuto (minor 9, review 2026-10-07).
                import re
                m = re.search(r"accepts (\d+)", detail)
                accepted = int(m.group(1)) if m else 0
                if 0 < accepted < page_size:
                    page_size = accepted
                    continue
            raise RoomRefusal(
                "La stanza «%s» ha rifiutato la consegna (HTTP %d): %s%s"
                % (settings.room_id, exc.code, detail,
                   (" — %d operazioni su %d erano GIÀ arrivate (idempotenti:"
                    " alla prossima consegna non si duplicano)"
                    % (start, len(ops))) if start else "")) from exc
        except Exception as exc:
            raise RoomRefusal(
                "Non ho potuto raggiungere il nodo (%s): %s. Consegnate "
                "%d operazioni su %d; le operazioni sono idempotenti — "
                "riprova tutto quando il nodo risponde."
                % (settings.server_url, exc, start, len(ops))) from exc
        if status != 200:
            raise RoomRefusal(
                "La stanza «%s» ha risposto HTTP %d alla pagina %d."
                % (settings.room_id, status, out.batches + 1))
        out.batches += 1
        out.applied += int(answer.get("applied") or 0)
        out.refused.extend(answer.get("refused") or [])
        start += len(page)
    return out


def deliver_site(conn_str, sito, settings=None, http: Http = _urllib_http,
                 lang=None):
    """us_table → stanza, nell'ordine che conta: configurazione, identità,
    traduzione, e SOLO POI la rete delle ops."""
    from . import site_rows, us_ops

    settings = settings or NodeSettings()
    if not settings.enforcing:
        missing = [n for n, v in ((SERVER_URL_VARIABLE, settings.server_url),
                                  (ROOM_ID_VARIABLE, settings.room_id))
                   if not v]
        raise RoomRefusal(
            "Nessuna stanza configurata: manca %s. Imposta server e stanza "
            "(env o campo del dialogo) — senza entrambi una consegna "
            "andrebbe dove nessuno ha scelto." % " e ".join(missing))
    probe = _probe_http if http is _urllib_http else http
    _require_identity(settings, probe)

    # I5 (review): un DB zoppo (us_table assente, PG giù, colonna driftata)
    # è una frase per l'utente, mai un traceback nel dialogo di QGIS.
    try:
        units, relationships, problems = site_rows.load(conn_str, sito)
    except Exception as exc:
        raise RoomRefusal(
            "Lettura di us_table fallita dal database (%s). Niente è stato "
            "consegnato." % exc) from exc
    made = us_ops.deliver(units, relationships, lang=lang)
    made.skipped.extend(problems)
    if not made.ops:
        out = Outcome(room_id=settings.room_id)
        out.skipped = list(made.skipped)
        out.counts = dict(made.counts)
        return out
    out = _deliver_ops(made.ops, settings, http)
    out.skipped = list(made.skipped)
    out.counts = dict(made.counts)
    log.info("[room] %s → %s (sito=%r)", settings.room_id, out.summary(), sito)
    return out


def rooms_door(server_url, http: Http = _probe_http):
    """La porta della UI delle stanze: /em/rooms/ dietro Caddy, /rooms/ sul
    nodo nudo. La prima che risponde 200."""
    base = server_url.rstrip("/")
    paths = ("/rooms/",) if base.endswith("/em") else ("/em/rooms/", "/rooms/")
    for path in paths:
        try:
            status, _body = http("GET", base + path, None, "")
        except Exception:
            continue
        if status == 200:
            return base + path
    return base + ("/rooms/" if base.endswith("/em") else "/em/rooms/")


def room_work_url(server_url, room_id, http: Http = _probe_http):
    """L'indirizzo stabile della stanza: la pagina *work* del nodo.

    `/em/work/?room=<id>` dietro Caddy, `/work/?room=<id>` sul nodo nudo:
    le pagine-verbo sono montate IN CIMA (main.py:5265 — «MOUNTED AT THE
    TOP, not nested under /rooms/»); /rooms/work/ risponde 200 ma è una
    shell i cui asset relativi 404ano (review 2026-10-07). Su nodo muto si
    restituisce comunque il candidato Caddy: il pannello mostrerà il SUO
    errore — mai un'eccezione qui, due sonde da 5 s al massimo.
    """
    import urllib.parse
    base = server_url.rstrip("/")
    query = "?room=%s" % urllib.parse.quote(room_id, safe="")
    paths = ("/work/",) if base.endswith("/em") \
        else ("/em/work/", "/work/")
    for path in paths:
        try:
            status, _body = http("GET", base + path, None, "")
        except Exception:
            continue
        if status == 200:
            return base + path + query
    return base + ("/work/" if base.endswith("/em") else "/em/work/") + query
