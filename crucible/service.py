"""Read-only local health and status service."""

from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from crucible import __version__


class Handler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        if self.path not in {"/health", "/status"}:
            self.send_error(404)
            return
        payload = {
            "status": "healthy",
            "service": "crucible-control",
            "version": __version__,
            "external_network": "disabled-by-compose",
        }
        body = json.dumps(payload).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args: object) -> None:
        return


def main() -> None:
    server = ThreadingHTTPServer(("0.0.0.0", 8080), Handler)  # noqa: S104
    server.serve_forever()


if __name__ == "__main__":
    main()
