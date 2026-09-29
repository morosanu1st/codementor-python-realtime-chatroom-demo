"""Minimal async WebSocket chatroom server."""

from __future__ import annotations

import asyncio
import logging
from typing import Dict

import websockets
from websockets.server import WebSocketServerProtocol

from .protocol import ProtocolError, decode, encode

HOST = "127.0.0.1"
PORT = 8765

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("chat")

# websocket -> display name (None until join)
clients: Dict[WebSocketServerProtocol, str | None] = {}


async def broadcast(message: dict, *, exclude: WebSocketServerProtocol | None = None) -> None:
    raw = encode(message)
    dead: list[WebSocketServerProtocol] = []
    for ws in list(clients):
        if ws is exclude:
            continue
        try:
            await ws.send(raw)
        except Exception:
            dead.append(ws)
    for ws in dead:
        await unregister(ws)


async def unregister(ws: WebSocketServerProtocol) -> None:
    name = clients.pop(ws, None)
    if name:
        log.info("leave: %s", name)
        await broadcast({"type": "system", "text": f"{name} left the chat"})


async def handle(ws: WebSocketServerProtocol) -> None:
    clients[ws] = None
    try:
        async for raw in ws:
            try:
                msg = decode(raw)
            except ProtocolError as exc:
                await ws.send(encode({"type": "error", "text": str(exc)}))
                continue

            name = clients.get(ws)
            if msg["type"] == "join":
                if name:
                    await ws.send(encode({"type": "error", "text": "already joined"}))
                    continue
                clients[ws] = msg["name"]
                log.info("join: %s", msg["name"])
                await ws.send(encode({"type": "system", "text": f"Welcome, {msg['name']}!"}))
                await broadcast(
                    {"type": "system", "text": f"{msg['name']} joined the chat"},
                    exclude=ws,
                )
            elif msg["type"] == "leave":
                await unregister(ws)
                break
            elif msg["type"] == "chat":
                if not name:
                    await ws.send(encode({"type": "error", "text": "join first"}))
                    continue
                await broadcast({"type": "chat", "name": name, "text": msg["text"]})
    except websockets.ConnectionClosed:
        pass
    finally:
        if ws in clients:
            await unregister(ws)


async def main() -> None:
    log.info("Chat server listening on ws://%s:%s", HOST, PORT)
    async with websockets.serve(handle, HOST, PORT):
        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())
