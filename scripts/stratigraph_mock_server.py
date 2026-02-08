#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
StratiGraph Mock Server — per testare il flusso di sync di PyArchInit.

Avvia un server HTTP locale che simula il micro-server WP4:
  - GET  /health              -> health check (usato dal ConnectivityMonitor)
  - POST /api/v1/bundles      -> riceve bundle ZIP (usato dal SyncOrchestrator)
  - GET  /api/v1/bundles      -> lista bundle ricevuti
  - GET  /                    -> pagina di stato

Uso:
    pip install fastapi uvicorn python-multipart
    python scripts/stratigraph_mock_server.py

    Oppure, senza FastAPI (fallback http.server integrato):
    python scripts/stratigraph_mock_server.py --simple

Il server ascolta su http://localhost:8080 (default).
"""
import argparse
import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

# Directory dove salvare i bundle ricevuti
DEFAULT_STORAGE = os.path.join(
    os.environ.get("PYARCHINIT_HOME", os.path.expanduser("~")),
    "stratigraph_mock_received"
)


def run_fastapi_server(host: str, port: int, storage_dir: str):
    """Server completo con FastAPI."""
    try:
        from fastapi import FastAPI, UploadFile, File, Request
        from fastapi.responses import HTMLResponse, JSONResponse
        import uvicorn
    except ImportError:
        print("FastAPI/uvicorn non installati. Installa con:")
        print("  pip install fastapi uvicorn python-multipart")
        print("\nOppure usa il server semplice: --simple")
        sys.exit(1)

    os.makedirs(storage_dir, exist_ok=True)
    app = FastAPI(title="StratiGraph Mock Server")

    # Registro bundle ricevuti (in-memory)
    received_bundles = []

    @app.get("/health")
    async def health():
        return {"status": "ok", "timestamp": datetime.now(timezone.utc).isoformat()}

    @app.post("/api/v1/bundles")
    async def upload_bundle(request: Request):
        content_type = request.headers.get("content-type", "")
        body = await request.body()

        if not body:
            return JSONResponse(
                status_code=400,
                content={"error": "Empty body"})

        # Genera nome file
        ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        sha = hashlib.sha256(body).hexdigest()[:12]
        filename = f"bundle_{ts}_{sha}.zip"
        filepath = os.path.join(storage_dir, filename)

        # Salva
        with open(filepath, "wb") as f:
            f.write(body)

        size_kb = len(body) / 1024
        entry = {
            "id": len(received_bundles) + 1,
            "filename": filename,
            "size_bytes": len(body),
            "sha256": hashlib.sha256(body).hexdigest(),
            "received_at": datetime.now(timezone.utc).isoformat(),
            "content_type": content_type,
        }
        received_bundles.append(entry)

        print(f"\n{'='*60}")
        print(f"  BUNDLE RICEVUTO #{entry['id']}")
        print(f"  File:    {filename}")
        print(f"  Size:    {size_kb:.1f} KB")
        print(f"  SHA-256: {entry['sha256']}")
        print(f"  Salvato: {filepath}")
        print(f"{'='*60}\n")

        return JSONResponse(
            status_code=201,
            content={
                "status": "accepted",
                "bundle_id": entry["id"],
                "filename": filename,
                "sha256": entry["sha256"],
            })

    @app.get("/api/v1/bundles")
    async def list_bundles():
        return {"bundles": received_bundles, "total": len(received_bundles)}

    @app.get("/", response_class=HTMLResponse)
    async def index():
        rows = ""
        for b in reversed(received_bundles):
            rows += (f"<tr><td>{b['id']}</td><td>{b['filename']}</td>"
                     f"<td>{b['size_bytes']}</td>"
                     f"<td>{b['received_at']}</td></tr>\n")
        if not rows:
            rows = '<tr><td colspan="4">Nessun bundle ricevuto</td></tr>'

        return f"""
        <html>
        <head><title>StratiGraph Mock Server</title>
        <style>
            body {{ font-family: sans-serif; margin: 2em; }}
            table {{ border-collapse: collapse; width: 100%; }}
            th, td {{ border: 1px solid #ccc; padding: 8px; text-align: left; }}
            th {{ background: #2E7D32; color: white; }}
            .status {{ color: #2E7D32; font-weight: bold; }}
        </style>
        </head>
        <body>
            <h1>StratiGraph Mock Server</h1>
            <p>Status: <span class="status">ONLINE</span></p>
            <p>Storage: <code>{storage_dir}</code></p>
            <h2>Bundle ricevuti ({len(received_bundles)})</h2>
            <table>
                <tr><th>ID</th><th>File</th><th>Size (bytes)</th><th>Ricevuto</th></tr>
                {rows}
            </table>
            <h2>Endpoints</h2>
            <ul>
                <li><code>GET /health</code> — health check</li>
                <li><code>POST /api/v1/bundles</code> — upload bundle ZIP</li>
                <li><code>GET /api/v1/bundles</code> — lista bundle (JSON)</li>
            </ul>
        </body>
        </html>
        """

    print(f"\nStratiGraph Mock Server")
    print(f"  URL:     http://{host}:{port}")
    print(f"  Health:  http://{host}:{port}/health")
    print(f"  Upload:  POST http://{host}:{port}/api/v1/bundles")
    print(f"  Storage: {storage_dir}")
    print(f"  Web UI:  http://{host}:{port}/")
    print()

    uvicorn.run(app, host=host, port=port)


def run_simple_server(host: str, port: int, storage_dir: str):
    """Server minimale con http.server (nessuna dipendenza esterna)."""
    from http.server import HTTPServer, BaseHTTPRequestHandler

    os.makedirs(storage_dir, exist_ok=True)
    received_count = 0

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path == "/health":
                self._json_response(200, {
                    "status": "ok",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                })
            else:
                self._json_response(200, {
                    "message": "StratiGraph Mock Server (simple mode)",
                    "endpoints": ["/health", "POST /api/v1/bundles"]
                })

        def do_POST(self):
            nonlocal received_count
            if self.path == "/api/v1/bundles":
                length = int(self.headers.get("Content-Length", 0))
                body = self.rfile.read(length)

                ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
                sha = hashlib.sha256(body).hexdigest()[:12]
                filename = f"bundle_{ts}_{sha}.zip"
                filepath = os.path.join(storage_dir, filename)

                with open(filepath, "wb") as f:
                    f.write(body)

                received_count += 1
                size_kb = len(body) / 1024

                print(f"\n  BUNDLE #{received_count}: {filename} "
                      f"({size_kb:.1f} KB) -> {filepath}")

                self._json_response(201, {
                    "status": "accepted",
                    "bundle_id": received_count,
                    "filename": filename,
                })
            else:
                self._json_response(404, {"error": "Not found"})

        def _json_response(self, code, data):
            body = json.dumps(data).encode()
            self.send_response(code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, format, *args):
            # Mostra solo le richieste importanti
            if "/health" not in str(args):
                print(f"  [{datetime.now().strftime('%H:%M:%S')}] {args[0]}")

    print(f"\nStratiGraph Mock Server (simple mode)")
    print(f"  URL:     http://{host}:{port}")
    print(f"  Health:  http://{host}:{port}/health")
    print(f"  Upload:  POST http://{host}:{port}/api/v1/bundles")
    print(f"  Storage: {storage_dir}")
    print(f"\n  (Per la web UI installa FastAPI: pip install fastapi uvicorn python-multipart)\n")

    server = HTTPServer((host, port), Handler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer fermato.")


def main():
    parser = argparse.ArgumentParser(
        description="StratiGraph Mock Server per testare il sync di PyArchInit")
    parser.add_argument("--host", default="localhost", help="Host (default: localhost)")
    parser.add_argument("--port", type=int, default=8080, help="Porta (default: 8080)")
    parser.add_argument("--storage", default=DEFAULT_STORAGE,
                        help=f"Directory per salvare i bundle (default: {DEFAULT_STORAGE})")
    parser.add_argument("--simple", action="store_true",
                        help="Usa http.server invece di FastAPI (nessuna dipendenza)")
    args = parser.parse_args()

    if args.simple:
        run_simple_server(args.host, args.port, args.storage)
    else:
        try:
            import fastapi
            import uvicorn
            run_fastapi_server(args.host, args.port, args.storage)
        except ImportError:
            print("FastAPI non trovato, uso il server semplice...")
            print("(Installa con: pip install fastapi uvicorn python-multipart)\n")
            run_simple_server(args.host, args.port, args.storage)


if __name__ == "__main__":
    main()
