"""Check the local CRUCIBLE control service."""

from __future__ import annotations

import json
from urllib.request import urlopen

with urlopen("http://127.0.0.1:8080/health", timeout=3) as response:
    payload = json.loads(response.read())
    if payload.get("status") != "healthy":
        raise SystemExit("service unhealthy")
    print(json.dumps(payload, sort_keys=True))
