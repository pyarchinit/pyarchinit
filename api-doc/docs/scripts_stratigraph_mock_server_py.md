# scripts/stratigraph_mock_server.py

## Overview

This file contains 12 documented elements.

## Classes

### Handler

*No description available.*
A local `BaseHTTPRequestHandler` subclass that implements a lightweight mock HTTP server for StratiGraph bundle ingestion. It handles `GET` requests on `/health` (returning a UTC timestamp and status) and on the root path (returning available endpoints), and `POST` requests on `/api/v1/bundles` (reading the request body, persisting it as a timestamped, SHA-256-named ZIP file under `storage_dir`, incrementing a shared `received_count`, and responding with `201 Accepted`). The `_json_response` helper serialises a dictionary to JSON and writes it with the appropriate headers, while `log_message` suppresses health-check noise from the default access log.

**Inherits from**: BaseHTTPRequestHandler

#### Methods

##### do_GET(self)

*No description available.*
Handles incoming HTTP GET requests by routing based on the request path. Requests to `/health` receive a JSON response containing a status of `"ok"` and the current UTC timestamp; all other paths receive a JSON response identifying the server as a StratiGraph Mock Server in simple mode, along with a list of available endpoints (`/health` and `POST /api/v1/bundles`).

##### do_POST(self)

Handles HTTP POST requests by routing on the request path. When the path is `/api/v1/bundles`, it reads the request body, writes it to disk as a ZIP file named with a UTC timestamp and a 12-character SHA-256 prefix, increments the received bundle counter, and returns a `201` JSON response containing the assigned `bundle_id` and `filename`. Any other path returns a `404` JSON error response.

##### log_message(self, format)

*No description available.*
Overrides the default HTTP server request logging behavior to suppress noise from `/health` endpoint polling. For any request that does not contain `/health` in its arguments, it prints the first argument (the request line) to standard output, prefixed with the current time formatted as `HH:MM:SS`. The `format` parameter is accepted but not used.

## Functions

### run_fastapi_server(host, port, storage_dir)

Server completo con FastAPI.

**Parameters:**
- `host: str`
- `port: int`
- `storage_dir: str`

### run_simple_server(host, port, storage_dir)

Server minimale con http.server (nessuna dipendenza esterna).

**Parameters:**
- `host: str`
- `port: int`
- `storage_dir: str`

### main()

*No description available.*
Entry point for the StratiGraph Mock Server, which parses command-line arguments to configure the host, port, and storage directory. Depending on the `--simple` flag, it starts either a `http.server`-based server via `run_simple_server` or a FastAPI/Uvicorn server via `run_fastapi_server`. If FastAPI or Uvicorn are not installed and `--simple` is not specified, it falls back automatically to the simple server.

### health()

*No description available.*
**Endpoint:** `GET /health`

Returns the current health status of the application as a JSON object containing a static `"status"` field set to `"ok"` and a `"timestamp"` field reflecting the current UTC date and time in ISO 8601 format. This endpoint requires no parameters and serves as a liveness check for the service.

### upload_bundle(request)

Handles `POST /api/v1/bundles` requests by receiving a raw request body and persisting it to disk as a ZIP file with a name composed of a UTC timestamp and the first 12 characters of its SHA-256 hash. Returns a `400` response if the body is empty; otherwise, records bundle metadata (id, filename, size in bytes, full SHA-256 digest, receipt timestamp, and content type) in the in-memory `received_bundles` list and writes a summary to stdout. On success, returns a `201 JSON` response containing `status`, `bundle_id`, `filename`, and `sha256`.

**Parameters:**
- `request: Request`

### list_bundles()

*No description available.*
**Route:** `GET /api/v1/bundles`

Returns a JSON object containing all received bundles and a count of the total number of entries. The response includes two fields: `bundles`, which holds the list of received bundle records, and `total`, which reflects the current length of that list.

### index()

*No description available.*
Handles `GET /` requests and returns an HTML dashboard for the StratiGraph Mock Server. The page displays the server status, the configured storage directory, and a table of all received bundles (id, filename, size in bytes, and reception timestamp) in reverse chronological order. If no bundles have been received, a placeholder row is shown; the page also lists the available API endpoints.

