# A Keycloak client for pyArchInit — for WP4

pyArchInit (the QGIS plugin) signs in to a StratiGraph node as a **native desktop
app**: Authorization Code + PKCE (S256), the code coming back to a one-shot
listener on `http://127.0.0.1:<port>/` (RFC 8252). Today it uses the client the
node names in `/v1/auth-config` (`native_client_id`, `em-tools` on the dev
stack). A client of its own lets the node and the logs tell pyArchInit from EM
Tools.

## The client

[`keycloak-client-pyarchinit.json`](keycloak-client-pyarchinit.json) — the same
shape and protocol mappers as `em-tools` in the dev-stack realm
(`dev-stack/keycloak/realm-em-dev.json`): public, standard flow only, PKCE S256,
one redirect URI `http://127.0.0.1/` (Keycloak admits any loopback port for it),
access token 900 s, audience `em-server` (and `em-chatbot`), `orcid`, `em_idp`
and `em_auth_reported` claims.

Import it into the node's realm, e.g. inside the Keycloak container:

```bash
kcadm.sh config credentials --server http://localhost:8080/auth --realm master \
    --user "$KEYCLOAK_ADMIN" --password "$KEYCLOAK_ADMIN_PASSWORD"
kcadm.sh create clients -r <realm> -f keycloak-client-pyarchinit.json
```

(The description is kept under 255 characters: Keycloak refuses a longer one
with an `unknown_error`.)

## How pyArchInit picks the client

1. the setting `pyArchInit/stratigraph/client_id` in QGIS, when set;
2. else `native_clients.pyarchinit` from `/v1/auth-config`, **if the node
   publishes such a map** — a proposal: one native client per tool, e.g.
   `{"native_client_id": "em-tools", "native_clients": {"em-tools": "em-tools",
   "pyarchinit": "pyarchinit"}}`;
3. else `native_client_id`, as today.

## Verified (26 Nov 2026, dev-stack, Keycloak 24)

Client imported with `kcadm`; a full sign-in through pyArchInit's own code as
`pyarchinit`: token `azp = pyarchinit`, audience `em-server`, `/v1/whoami`
answers (`may_create: true`), the refresh-token renewal stays on `pyarchinit`.
