"""JSON chat protocol helpers.

Message shapes:
  {"type": "join", "name": "Alice"}
  {"type": "leave"}
  {"type": "chat", "text": "hello"}
  {"type": "system", "text": "..."}   # server -> clients
  {"type": "error", "text": "..."}    # server -> client
  {"type": "chat", "name": "Alice", "text": "hello"}  # broadcast
"""

from __future__ import annotations

import json
from typing import Any


ALLOWED_CLIENT_TYPES = {"join", "leave", "chat"}


class ProtocolError(ValueError):
    """Raised when a client message is invalid."""


def encode(message: dict[str, Any]) -> str:
    return json.dumps(message, ensure_ascii=False)


def decode(raw: str) -> dict[str, Any]:
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ProtocolError("invalid JSON") from exc
    if not isinstance(data, dict):
        raise ProtocolError("message must be a JSON object")
    msg_type = data.get("type")
    if msg_type not in ALLOWED_CLIENT_TYPES:
        raise ProtocolError(f"unknown type: {msg_type!r}")
    if msg_type == "join":
        name = data.get("name")
        if not isinstance(name, str) or not name.strip():
            raise ProtocolError("join requires a non-empty name")
        data["name"] = name.strip()[:32]
    if msg_type == "chat":
        text = data.get("text")
        if not isinstance(text, str) or not text.strip():
            raise ProtocolError("chat requires non-empty text")
        data["text"] = text.strip()[:500]
    return data
