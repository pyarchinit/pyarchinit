"""node_client: the native sign-in against a node, measured on a fake node.

The fake plays both the node (``/v1/auth-config``) and its identity service:
the authorization endpoint redirects to the loopback with a code, the token
endpoint gives a token only to the verifier that matches the S256 challenge
and only when no client secret is sent.
"""
from __future__ import annotations

import base64
import hashlib
import http.server
import json
import threading
import urllib.parse
import urllib.request

import pytest

from modules.stratigraph import node_client as NC


class _FakeNode:
    def __init__(self, *, wrong_state=False):
        self.challenge = None
        self.wrong_state = wrong_state
        self.token_requests = []
        fake = self

        class Handler(http.server.BaseHTTPRequestHandler):
            def log_message(self, *a):
                pass

            def _send(self, code, body, headers=None):
                self.send_response(code)
                for k, v in (headers or {}).items():
                    self.send_header(k, v)
                self.end_headers()
                if body:
                    self.wfile.write(body)

            def do_GET(self):  # noqa: N802
                url = urllib.parse.urlparse(self.path)
                q = {k: v[0] for k, v in urllib.parse.parse_qs(url.query).items()}
                if url.path == "/em/v1/auth-config":
                    base = f"http://127.0.0.1:{fake.port}"
                    cfg = {"issuer": base, "client_id": "em-console",
                           "native_client_id": "em-tools", "scope": "openid",
                           "authorization_endpoint": base + "/auth",
                           "token_endpoint": base + "/token"}
                    return self._send(200, json.dumps(cfg).encode(),
                                      {"Content-Type": "application/json"})
                if url.path == "/auth":
                    assert q["code_challenge_method"] == "S256"
                    assert q["client_id"] == "em-tools"
                    fake.challenge = q["code_challenge"]
                    state = "forged" if fake.wrong_state else q["state"]
                    back = q["redirect_uri"] + "?" + urllib.parse.urlencode(
                        {"code": "the-code", "state": state})
                    return self._send(302, b"", {"Location": back})
                if url.path == "/em/v1/whoami":
                    return self._send(200, json.dumps(
                        {"orcid": "dev", "may_create": True}).encode())
                return self._send(404, b"")

            def do_POST(self):  # noqa: N802
                length = int(self.headers.get("Content-Length") or 0)
                form = dict(urllib.parse.parse_qsl(self.rfile.read(length).decode()))
                fake.token_requests.append(form)
                digest = hashlib.sha256(form["code_verifier"].encode()).digest()
                ok = (base64.urlsafe_b64encode(digest).rstrip(b"=").decode() == fake.challenge
                      and form["code"] == "the-code" and "client_secret" not in form)
                if not ok:
                    return self._send(400, json.dumps({"error": "invalid_grant"}).encode())
                return self._send(200, json.dumps(
                    {"access_token": "AT", "refresh_token": "RT", "expires_in": 300}).encode())

        self.server = http.server.HTTPServer(("127.0.0.1", 0), Handler)
        self.port = self.server.server_port
        threading.Thread(target=self.server.serve_forever, daemon=True).start()

    @property
    def node(self):
        return f"http://127.0.0.1:{self.port}/em"

    def close(self):
        self.server.shutdown()
        self.server.server_close()


def _browser(url):
    """What a browser does: follow the redirect back to the loopback."""
    threading.Thread(target=lambda: urllib.request.urlopen(url, timeout=10).read(),
                     daemon=True).start()


@pytest.fixture()
def fake():
    node = _FakeNode()
    yield node
    node.close()


def test_sign_in_with_pkce_gets_the_token(fake):
    tokens = NC.sign_in(fake.node, open_browser=_browser, timeout=10)
    assert tokens["access_token"] == "AT"
    form = fake.token_requests[-1]
    assert form["grant_type"] == "authorization_code"
    assert form["client_id"] == "em-tools"
    assert form["redirect_uri"].startswith("http://127.0.0.1:") and form["redirect_uri"].endswith("/")
    assert "client_secret" not in form


def test_a_code_with_another_state_is_refused():
    node = _FakeNode(wrong_state=True)
    try:
        with pytest.raises(NC.NodeError, match="state did not match"):
            NC.sign_in(node.node, open_browser=_browser, timeout=10)
        assert node.token_requests == []       # never exchanged
    finally:
        node.close()


def test_whoami_and_node_address(fake):
    assert NC.whoami(fake.node + "/", "AT")["may_create"] is True
    with pytest.raises(NC.NodeError):
        NC.node_base("em.localhost:8443/em")


def test_pkce_pair_is_s256():
    verifier, challenge = NC.pkce_pair()
    assert 43 <= len(verifier) <= 128
    digest = hashlib.sha256(verifier.encode()).digest()
    assert challenge == base64.urlsafe_b64encode(digest).rstrip(b"=").decode()


def test_a_database_file_is_never_uploaded():
    """The site's GIS footprint points at the whole pyArchInit database: kept as
    a reference, so the room never receives the other sites' records."""
    rows = [{"id": "r1", "path": "/data/pyarchinit_db.sqlite"},
            {"id": "r2", "path": "/data/layers.GPKG"},
            {"id": "r3", "path": "/data/foto/US1.jpg"},
            {"id": "r4", "path": None}]
    assert NC.database_rows(rows) == {"r1": "reference", "r2": "reference"}
