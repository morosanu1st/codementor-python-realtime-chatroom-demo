# Python Real-Time Chatroom Demo

Small, complete **client/server chatroom** demo for Codementor freelance delivery practice.

Features:
- Join / leave with a **username**
- Broadcast messages to all connected users
- Simple **HTML UI** (browser) plus optional **CLI client**
- Basic **error handling** (empty names, disconnects, bad JSON)
- **Unit tests** for message parsing / protocol helpers
- Clear run instructions

Stack: Python 3.9+, `websockets`, stdlib `http.server` for the static UI.

## Architecture (how I'd deliver)

```
Browser / CLI  --WebSocket-->  ChatServer
                                 |- registry of connections
                                 |- join / leave / chat handlers
                                 |- broadcast fan-out
Static HTML served on :8765 (or open file:// / separate static port)
```

Handoff checklist I use with clients:
1. Agree on protocol (JSON messages, fields, error codes)
2. Server concurrency model (async event loop here)
3. Tests for parsing and edge cases
4. README + one-command run
5. Optional next steps: auth, rooms, persistence, rate limits

## Quick start

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# terminal 1 — WebSocket server
python3 -m server.chat_server

# terminal 2 — optional static file server for the UI
python3 -m http.server 8080 --directory client

# open http://localhost:8080 in a browser
# or use the CLI client:
python3 -m client.cli_client --name Alice
```

Default WebSocket URL: `ws://127.0.0.1:8765`

## Tests

```bash
python3 -m pytest tests/ -v
# or without pytest:
python3 -m unittest discover -s tests -v
```

## Project layout

```
server/chat_server.py   # async WebSocket chat server
server/protocol.py      # message encode/decode helpers
client/index.html       # minimal browser UI
client/cli_client.py    # optional terminal client
tests/test_protocol.py  # protocol unit tests
```

Keep it small on purpose — enough to demo real-time messaging, concurrency, and a clean handoff, without overbuilding.
