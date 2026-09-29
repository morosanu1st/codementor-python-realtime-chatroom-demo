"""Optional CLI chat client."""

from __future__ import annotations

import argparse
import asyncio
import json
import sys

import websockets


async def run(url: str, name: str) -> None:
    async with websockets.connect(url) as ws:
        await ws.send(json.dumps({"type": "join", "name": name}))

        async def reader() -> None:
            async for raw in ws:
                try:
                    data = json.loads(raw)
                except json.JSONDecodeError:
                    print(raw)
                    continue
                if data.get("type") == "chat":
                    print(f"{data.get('name')}: {data.get('text')}")
                elif data.get("type") in {"system", "error"}:
                    print(f"[{data['type']}] {data.get('text')}")
                else:
                    print(data)

        async def writer() -> None:
            loop = asyncio.get_event_loop()
            while True:
                line = await loop.run_in_executor(None, sys.stdin.readline)
                if not line:
                    break
                text = line.rstrip("\n")
                if text.lower() in {"/quit", "/leave"}:
                    await ws.send(json.dumps({"type": "leave"}))
                    break
                if text.strip():
                    await ws.send(json.dumps({"type": "chat", "text": text}))

        await asyncio.wait(
            [asyncio.create_task(reader()), asyncio.create_task(writer())],
            return_when=asyncio.FIRST_COMPLETED,
        )


def main() -> None:
    parser = argparse.ArgumentParser(description="CLI chat client")
    parser.add_argument("--url", default="ws://127.0.0.1:8765")
    parser.add_argument("--name", required=True)
    args = parser.parse_args()
    asyncio.run(run(args.url, args.name))


if __name__ == "__main__":
    main()
