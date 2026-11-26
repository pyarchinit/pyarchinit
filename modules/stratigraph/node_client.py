"""pyArchInit as a correspondent of a StratiGraph node — Phase 3, minimal.

The node is StratiGraph Server (StratiGraph-ECCCH/stratigraph-server): rooms
reached over REST, identity from the node's Keycloak. pyArchInit does two
things with it, and invents neither:

* **signs in as a native app** — Authorization Code + PKCE (S256) against the
  node's own realm, the client the node names in ``/v1/auth-config``
  (``native_client_id``), the code coming back to a one-shot listener on
  ``http://127.0.0.1:<any port>/`` (RFC 8252 §7.3). No client secret, no
  password typed into pyArchInit, the token kept in memory only. Same contract
  as EM Tools' «Open in…» sign-in;
* **brings a site into a room** — the site's graph exported as em.json by the
  plugin's own exporter (``em_export.export_site``), then
  ``s3dgraphy.api.room_import``: the one engine EMStudio and EM Tools use to
  create the room, upload the files once and seat the graph as operations.

Qt-free and stdlib-only on purpose: the dialog and the command line call the
same functions, and the suite runs without QGIS. TLS goes through s3dgraphy's
``trust`` context — the computer's trusted roots, never verification off.
"""
from __future__ import annotations

import base64
import hashlib
import http.server
import json
import secrets
import threading
import urllib.error
import urllib.parse
import urllib.request
import webbrowser
from typing import Any, Callable, Dict, Optional

#: the redirect path the node's native client registers (port ignored, path exact)
LOOPBACK_PATH = "/"


class NodeError(RuntimeError):
    """A node answered no, or could not be reached — worded for a person."""


def trust_ca_file(path: str) -> None:
    """Also trust ``path`` (a PEM root, e.g. a dev or field node's local CA) for
    every call to a node — ours and s3dgraphy's, which share one context.
    Verification is never turned off: this ADDS a root, for this process only."""
    from s3dgraphy.room_import import trust
    trust.context().load_verify_locations(cafile=path)


def _open(request: urllib.request.Request, timeout: float):
    try:
        from s3dgraphy.room_import.trust import urlopen
    except ImportError:                                  # library absent: stdlib TLS
        urlopen = urllib.request.urlopen
    return urlopen(request, timeout=timeout)


def _json(request: urllib.request.Request, timeout: float = 30.0) -> Dict[str, Any]:
    try:
        with _open(request, timeout) as answer:
            return json.loads(answer.read() or b"{}")
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", "replace")[:300]
        try:
            detail = json.loads(detail).get("detail") or detail
        except (ValueError, AttributeError):
            pass
        raise NodeError(f"{request.full_url} → {exc.code}: {detail}") from None
    except urllib.error.URLError as exc:
        raise NodeError(f"{request.full_url} unreachable: {exc.reason}") from None


def node_base(url: str) -> str:
    """The node's API base as people write it, normalised: no trailing slash."""
    url = (url or "").strip().rstrip("/")
    if not url.startswith(("https://", "http://")):
        raise NodeError(f"{url!r} is not a node address (https://…)")
    return url


def auth_config(node: str, timeout: float = 10.0) -> Dict[str, Any]:
    """How to sign in to this node (no secret in it, by construction)."""
    config = _json(urllib.request.Request(f"{node_base(node)}/v1/auth-config"), timeout)
    if not config.get("token_endpoint") or not config.get("authorization_endpoint"):
        raise NodeError(f"{node} declares no sign-in: its identity service is off")
    return config


def client_of(config: Dict[str, Any]) -> str:
    """The client a native app signs in as: the one the node names for it."""
    return str(config.get("native_client_id") or config.get("client_id") or "")


def pkce_pair() -> tuple:
    """(verifier, S256 challenge) — never the ``plain`` method."""
    verifier = secrets.token_urlsafe(64)[:96]
    digest = hashlib.sha256(verifier.encode("ascii")).digest()
    return verifier, base64.urlsafe_b64encode(digest).rstrip(b"=").decode("ascii")


def exchange_code(config: Dict[str, Any], *, code: str, verifier: str,
                  redirect_uri: str, client_id: str) -> Dict[str, Any]:
    """The authorization code for tokens. A public client sends no secret."""
    body = urllib.parse.urlencode({
        "grant_type": "authorization_code", "code": code,
        "redirect_uri": redirect_uri, "client_id": client_id,
        "code_verifier": verifier}).encode()
    return _json(urllib.request.Request(
        config["token_endpoint"], data=body, method="POST",
        headers={"Content-Type": "application/x-www-form-urlencoded"}))


class SignIn:
    """One sign-in: ``start()`` gives the page to open, ``wait()`` the tokens.

    The listener takes exactly one request on the loopback, checks ``state``
    (a code delivered with another state is not one this session asked for)
    and is closed whatever happens.
    """

    def __init__(self, node: str, *, open_browser: Optional[Callable[[str], Any]] = webbrowser.open,
                 timeout: float = 300.0):
        self.node = node_base(node)
        self.open_browser = open_browser
        self.timeout = timeout
        self.config = auth_config(self.node)
        self.client_id = client_of(self.config)
        if not self.client_id:
            raise NodeError(f"{self.node} names no client for a desktop sign-in")
        self._got: Dict[str, str] = {}
        self._done = threading.Event()
        self._server: Optional[http.server.HTTPServer] = None
        self.redirect_uri = ""

    def start(self) -> str:
        session = self

        class Handler(http.server.BaseHTTPRequestHandler):
            def do_GET(self):  # noqa: N802 — http.server's name
                query = urllib.parse.urlparse(self.path).query
                session._got = {k: v[0] for k, v in urllib.parse.parse_qs(query).items()}
                page = ("<html><body style='font-family:sans-serif'><h2>pyArchInit</h2>"
                        "<p>Sign-in received. You can close this page and go back to QGIS.</p>"
                        "</body></html>").encode()
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.end_headers()
                self.wfile.write(page)
                session._done.set()

            def log_message(self, *args):        # quiet: no tokens or codes in logs
                pass

        self._server = http.server.HTTPServer(("127.0.0.1", 0), Handler)
        self.redirect_uri = f"http://127.0.0.1:{self._server.server_port}{LOOPBACK_PATH}"
        self._verifier, challenge = pkce_pair()
        self._state = secrets.token_urlsafe(24)
        url = self.config["authorization_endpoint"] + "?" + urllib.parse.urlencode({
            "response_type": "code", "client_id": self.client_id,
            "redirect_uri": self.redirect_uri, "scope": self.config.get("scope") or "openid",
            "state": self._state, "code_challenge": challenge,
            "code_challenge_method": "S256"})
        threading.Thread(target=self._server.handle_request, daemon=True).start()
        if self.open_browser:
            self.open_browser(url)
        return url

    def wait(self) -> Dict[str, Any]:
        try:
            if not self._done.wait(self.timeout):
                raise NodeError("sign-in not completed in time: nothing was signed in")
        finally:
            if self._server is not None:
                self._server.server_close()
        got = self._got
        if got.get("error"):
            raise NodeError(f"sign-in refused: {got.get('error_description') or got['error']}")
        if got.get("state") != self._state:
            raise NodeError("the sign-in state did not match: refusing a code this "
                            "session did not ask for")
        if not got.get("code"):
            raise NodeError("no authorization code came back")
        tokens = exchange_code(self.config, code=got["code"], verifier=self._verifier,
                               redirect_uri=self.redirect_uri, client_id=self.client_id)
        if not tokens.get("access_token"):
            raise NodeError("the node gave no access token")
        return tokens


def sign_in(node: str, **kwargs) -> Dict[str, Any]:
    """Open the node's sign-in page and wait for the tokens."""
    session = SignIn(node, **kwargs)
    session.start()
    return session.wait()


def refresh_tokens(config: Dict[str, Any], *, refresh_token: str,
                   client_id: str) -> Dict[str, Any]:
    """New tokens for the refresh token — the same public client, no secret."""
    body = urllib.parse.urlencode({
        "grant_type": "refresh_token", "refresh_token": refresh_token,
        "client_id": client_id}).encode()
    return _json(urllib.request.Request(
        config["token_endpoint"], data=body, method="POST",
        headers={"Content-Type": "application/x-www-form-urlencoded"}))


class NodeSession:
    """A signed-in node: the tokens, kept in memory, renewed before they expire.

    The node's access token lives minutes (the dev realm issues five); the
    refresh token it gives with it lives the session. ``access_token()`` is
    what every call asks for: the current token, or a renewed one when fewer
    than ``margin`` seconds are left. A refused renewal (session ended on the
    node, refresh token revoked) is said as «sign in again», never retried.
    """

    def __init__(self, node: str, tokens: Dict[str, Any], *, config: Optional[Dict[str, Any]] = None,
                 client_id: Optional[str] = None, margin: float = 30.0, clock=None):
        import time
        self.node = node_base(node)
        self._clock = clock or time.monotonic
        self.config = config or auth_config(self.node)
        self.client_id = client_id or client_of(self.config)
        self.margin = margin
        self.renewals = 0
        self._take(tokens)

    def _take(self, tokens: Dict[str, Any]) -> None:
        if not tokens.get("access_token"):
            raise NodeError("the node gave no access token")
        self._access = tokens["access_token"]
        self._refresh = tokens.get("refresh_token") or getattr(self, "_refresh", None)
        self._expires_at = self._clock() + float(tokens.get("expires_in") or 300)

    @classmethod
    def sign_in(cls, node: str, **kwargs) -> "NodeSession":
        """Browser sign-in, then a session that renews itself."""
        running = SignIn(node, **kwargs)
        running.start()
        return cls(node, running.wait(), config=running.config, client_id=running.client_id)

    def expires_in(self) -> float:
        return self._expires_at - self._clock()

    def access_token(self) -> str:
        if self.expires_in() > self.margin:
            return self._access
        if not self._refresh:
            raise NodeError("the access token expired and the node gave no refresh token: "
                            "sign in again")
        try:
            tokens = refresh_tokens(self.config, refresh_token=self._refresh,
                                    client_id=self.client_id)
        except NodeError as exc:
            raise NodeError(f"the session on the node ended ({exc}): sign in again") from None
        self._take(tokens)
        self.renewals += 1
        return self._access


def whoami(node: str, token: str) -> Dict[str, Any]:
    """Who this token says you are, on this node (and whether you may create rooms)."""
    return _json(urllib.request.Request(
        f"{node_base(node)}/v1/whoami", headers={"Authorization": f"Bearer {token}"}))


#: files that are a whole database: never uploaded, only referenced. The site's
#: GIS footprint is a resource whose path is the pyArchInit database itself —
#: uploading it would send every site and every record to the room, not the
#: one site chosen (measured 26 Nov 2026: the sample site planned the 12.6 MB
#: sample database as its one upload).
DATABASE_SUFFIXES = (".sqlite", ".sqlite3", ".db", ".spatialite", ".gpkg")


def database_rows(rows) -> Dict[str, str]:
    """``per_item`` choices keeping every database file as a reference."""
    from s3dgraphy.room_import.inventory import CHOICE_REFERENCE
    return {row["id"]: CHOICE_REFERENCE for row in rows
            if str(row.get("path") or "").lower().endswith(DATABASE_SUFFIXES)}


def send_site(connection_url: str, site: str, *, node: str, room: str, token: str,
              workdir: str, title: Optional[str] = None, per_saggio: Optional[bool] = False,
              dry_run: bool = False) -> Dict[str, Any]:
    """The site's graph into ``room`` on ``node``: exported, then brought in.

    s3dgraphy's room import in its three steps — the plan, the choices (every
    database file stays a reference, see ``DATABASE_SUFFIXES``), the import.
    The site goes as ONE graph by default (``per_saggio=False``): the room
    import seats each graph's nodes and edges but not the links between
    graphs, and a site split by trench lost its cross-trench relations
    (measured 26 Nov 2026: 32 links in the export, 0 in the room).

    Returns its report plus what was exported (``em_json``, ``nodes``,
    ``edges``, ``export_warnings``) and ``kept_as_reference``. ``dry_run``:
    the plan only, nothing written on the node.
    """
    import time

    from modules.s3dgraphy import em_export
    from s3dgraphy import room_import as RI
    from s3dgraphy.room_import import node as nodeio

    em_json, n_nodes, n_edges, warnings = em_export.export_site(
        connection_url, site, workdir, per_saggio=per_saggio)
    run = RI.prepare(em_json, node=node_base(node), room=room, title=title or site,
                     token=token, dry_run=dry_run)
    kept = database_rows(run["plan"]["rows"])
    if kept:
        RI.apply_choices(run, per_item=kept)
    if dry_run:
        report = RI.plan_report(run)
        report["requests"] = nodeio.seen_requests()
        report["seconds"] = round(time.monotonic() - run["t0"], 1)
    else:
        report = RI.execute(run)
    report = dict(report or {})
    report.update({"em_json": em_json, "nodes": n_nodes, "edges": n_edges,
                   "export_warnings": list(warnings or []),
                   "kept_as_reference": sorted(
                       row.get("path") for row in run["plan"]["rows"] if row["id"] in kept)})
    return report
