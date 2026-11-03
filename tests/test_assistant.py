# SPDX-License-Identifier: MIT
"""Protocolo HTTP sintetico; inferencia real e verificada separadamente."""
import contextlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import io
import json
import os
from pathlib import Path
import tempfile
import threading
import unittest
from unittest.mock import patch
from official_core import local_ai
from official_core.assistant_cli import create_app, _display
from official_core.console import main


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def do_POST(self):
        self.server.received = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        self.send_response(self.server.code)
        if self.server.code == 302:
            self.send_header("Location", "https://example.invalid/private")
        self.end_headers()
        self.wfile.write(self.server.payload)


class AssistantTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve() / "workspace"

    def test_local_http_ignores_proxies_and_blocks_redirect(self):
        server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        server.code = 200
        server.payload = json.dumps({"done": True, "message": {"role": "assistant", "content": "Ola"}}).encode()
        threading.Thread(target=server.serve_forever, daemon=True).start()
        self.addCleanup(server.server_close)
        self.addCleanup(server.shutdown)
        messages = [{"role": "user", "content": "Oi"}]
        with patch.object(local_ai, "ENDPOINT", "http://127.0.0.1:" + str(server.server_port) + "/api/chat"), patch.dict(os.environ, {"http_proxy": "http://127.0.0.1:1", "no_proxy": ""}):
            self.assertEqual(local_ai.chat(messages, timeout=2), "Ola")
            self.assertEqual(server.received["messages"], messages)
            self.assertFalse(server.received["stream"])
            server.code = 302
            with self.assertRaisesRegex(local_ai.LocalAIError, "Redirecionamento"):
                local_ai.chat(messages, timeout=2)
            server.code = 404
            server.payload = b"private-error-example"
            with self.assertRaisesRegex(local_ai.LocalAIError, "Modelo nao encontrado") as error:
                local_ai.chat(messages, timeout=2)
            self.assertNotIn("private-error", str(error.exception))
            server.code = 200
            for payload in [b"invalid-json", b"x" * (local_ai.MAX_BYTES + 1), b"{}", b"[]", b"{\"done\":false}"]:
                server.payload = payload
                with self.assertRaises(local_ai.LocalAIError):
                    local_ai.chat(messages, timeout=2)

    def test_input_validation_precedes_http(self):
        with patch.object(local_ai, "build_opener", side_effect=AssertionError("network forbidden")):
            for messages in [[], [{}], [{"role": "tool", "content": "x"}], [{"role": "user", "content": "x" * 16001}]]:
                with self.assertRaises(local_ai.LocalAIError):
                    local_ai.chat(messages)
            for timeout in [0, 601, float("nan"), float("inf")]:
                with self.assertRaises(local_ai.LocalAIError):
                    local_ai.chat([{"role": "user", "content": "x"}], timeout=timeout)
            with self.assertRaises(local_ai.LocalAIError):
                local_ai.chat([{"role": "user", "content": "x"}], "cloud-model")

    def test_network_error_does_not_leak_details(self):
        with patch.object(local_ai, "build_opener") as opener:
            opener.return_value.open.side_effect = OSError("private-detail")
            with self.assertRaisesRegex(local_ai.LocalAIError, "Ollama indisponivel") as error:
                local_ai.chat([{"role": "user", "content": "x"}])
        self.assertNotIn("private-detail", str(error.exception))

    def test_templates_require_no_model(self):
        with patch.object(local_ai, "chat", side_effect=AssertionError("network forbidden")):
            for template in ["counter", "todo"]:
                result = create_app(self.root, template, template=template)
                self.assertIn("Content-Security-Policy", Path(result["path"]).read_text(encoding="utf-8"))
                self.assertFalse(result["apk"])
                self.assertFalse(result["executed"])
                self.assertEqual(result["source"], "offline_template")

    def test_existing_app_not_overwritten(self):
        result = create_app(self.root, "first")
        before = Path(result["path"]).read_bytes()
        with patch.object(local_ai, "chat", side_effect=AssertionError("network forbidden")), self.assertRaises(FileExistsError):
            create_app(self.root, "first", prompt="modify")
        self.assertEqual(Path(result["path"]).read_bytes(), before)

    def test_bad_paths_and_empty_prompt_leave_no_files(self):
        for name in ["../outside", "UPPER", "", "con"]:
            with self.assertRaises(ValueError):
                create_app(self.root, name)
        with self.assertRaises(ValueError):
            create_app(self.root, "valid", prompt=" " )
        self.assertFalse(self.root.exists())

    def test_generated_code_is_embedded_untrusted(self):
        raw = "<html><body><button>Oi</button><script>alert(1)</script></body></html>"
        with patch.object(local_ai, "chat", return_value=raw):
            result = create_app(self.root, "from-ai", prompt="Um botao")
        text = Path(result["path"]).read_text(encoding="utf-8")
        self.assertIn("sandbox=\"allow-scripts\"", text)
        self.assertNotIn("allow-same-origin", text)
        self.assertIn("&lt;script&gt;alert(1)&lt;/script&gt;", text)
        self.assertFalse(result["functional_tested"])
        self.assertFalse(result["executed"])

    def test_incomplete_html_not_saved(self):
        with patch.object(local_ai, "chat", return_value="<html><body>truncated"), self.assertRaises(local_ai.LocalAIError):
            create_app(self.root, "invalid", prompt="App")
        self.assertFalse(self.root.exists())

    def test_chat_cli_does_not_save_prompt(self):
        with patch.object(local_ai, "chat", return_value="Resposta local"), contextlib.redirect_stdout(io.StringIO()) as output:
            self.assertEqual(main(["--root", str(self.root), "chat", "private-prompt"]), 0)
        self.assertIn("Resposta local", output.getvalue())
        self.assertFalse(self.root.exists())

    def test_interactive_chat_exits_without_saving(self):
        with patch("builtins.input", side_effect=["Oi", "/sair"]), patch.object(local_ai, "chat", return_value="Ola"), contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(main(["--root", str(self.root), "chat"]), 0)
        self.assertFalse(self.root.exists())

    def test_app_cli_and_failures(self):
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(main(["--root", str(self.root), "app", "create", "counter"]), 0)
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(main(["--root", str(self.root), "app", "create", "counter"]), 1)
            with patch.object(local_ai, "chat", side_effect=local_ai.LocalAIError("offline")):
                self.assertEqual(main(["chat", "Oi"]), 1)

    def test_control_characters_removed(self):
        self.assertEqual(_display("a\x1bb\x00c\nd"), "abc\nd")


if __name__ == "__main__":
    unittest.main()
