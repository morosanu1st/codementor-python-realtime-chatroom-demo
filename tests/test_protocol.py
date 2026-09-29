"""Unit tests for chat protocol helpers."""

from __future__ import annotations

import unittest

from server.protocol import ProtocolError, decode, encode


class ProtocolTests(unittest.TestCase):
    def test_encode_roundtrip_fields(self) -> None:
        raw = encode({"type": "join", "name": "Alice"})
        self.assertIn("Alice", raw)

    def test_join_ok(self) -> None:
        msg = decode('{"type": "join", "name": "  Bob  "}')
        self.assertEqual(msg["name"], "Bob")

    def test_join_empty_name(self) -> None:
        with self.assertRaises(ProtocolError):
            decode('{"type": "join", "name": "   "}')

    def test_chat_ok(self) -> None:
        msg = decode('{"type": "chat", "text": "hi"}')
        self.assertEqual(msg["text"], "hi")

    def test_chat_empty(self) -> None:
        with self.assertRaises(ProtocolError):
            decode('{"type": "chat", "text": ""}')

    def test_bad_json(self) -> None:
        with self.assertRaises(ProtocolError):
            decode("not-json")

    def test_unknown_type(self) -> None:
        with self.assertRaises(ProtocolError):
            decode('{"type": "ping"}')


if __name__ == "__main__":
    unittest.main()
