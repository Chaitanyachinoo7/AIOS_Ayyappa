from __future__ import annotations

import hmac
import hashlib
import json
from typing import Any


def verify_hmac_sha256(*, secret: str, body: bytes, signature_header: str | None) -> bool:
    if not signature_header:
        return False

    candidate = signature_header.strip()
    if candidate.startswith("sha256="):
        candidate = candidate[len("sha256=") :]

    expected = hmac.new(secret.encode("utf-8"), msg=body, digestmod=hashlib.sha256).hexdigest()
    try:
        return hmac.compare_digest(expected, candidate)
    except Exception:
        return False


def safe_json_loads(body: bytes) -> dict[str, Any]:
    try:
        obj = json.loads(body.decode("utf-8"))
        if isinstance(obj, dict):
            return obj
        return {"_": obj}
    except Exception:
        return {"_raw": body.decode("utf-8", errors="replace")}

