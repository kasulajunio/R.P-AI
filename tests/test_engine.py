import contextlib
import io
import json
import os
import sqlite3
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from official_core.cli import main, menu
from official_core.engine import MasterEngine, SafetyError, sha256_file


class EngineTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="fabio-core-test-")
        self.addCleanup(self.temp.cleanup)
        self.parent = Path(self.temp.name).resolve()
        self.root = self.parent / "workspace"
        self.engine = MasterEngine(self.root)

    def invoke(self, *args):
        output = io.StringIO()
        errors = io.StringIO()
        with contextlib.redirect_stdout(output), contextlib.redirect_stderr(errors):
            status = main(["--root", str(self.root), *args])
        return status, output.getvalue(), errors.getvalue()

    def test_constructor_has_no_write(self):
        self.assertFalse(self.root.exists())

    def test_init_creates_five_modules(self):
        self.engine.setup_structure()
        for name in self.engine.modules.values():
            self.assertTrue((self.root / name).is_dir())

    def test_config_no_downloads(self):
        self.engine.setup_structure()
        config = json.loads((self.root / "core.json").read_text())
        self.assertFalse(config["network_enabled"])
        self.assertFalse(config["automatic_downloads"])

    def test_init_preserves_existing_config(self):
        self.engine.setup_structure()
        path = self.root / "core.json"
        path.write_text("CUSTOM", encoding="utf-8")
        self.engine.setup_structure()
        self.assertEqual(path.read_text(), "CUSTOM")

    def test_new_file_not_overwritten(self):
        self.assertTrue(self.engine._write_new("test.txt", "first"))
        self.assertFalse(self.engine._write_new("test.txt", "second"))
        self.assertEqual((self.root / "test.txt").read_text(), "first")

    def test_nonfile_destination_rejected(self):
        self.engine._mkdir("blocked.txt")
        with self.assertRaises(SafetyError):
            self.engine._write_new("blocked.txt", "x")

    def test_root_system_rejected(self):
        with self.assertRaises(SafetyError):
            MasterEngine(Path(self.parent.anchor))

    def test_root_parent_escape_rejected(self):
        with self.assertRaises(SafetyError):
            MasterEngine(self.parent / ".." / "escape")

    def test_invalid_paths_rejected(self):
        values = ["", ".", "..", "../bad", "a/../b", "/tmp/bad", "C:/bad", "a\\b", "a//b", "a/./b", "CON", "nul.txt", "COM1", "x.", "with space", "a\x00b"]
        for value in values:
            with self.subTest(value=value), self.assertRaises(SafetyError):
                self.engine.path(value)

    def test_portable_nested_path(self):
        self.assertEqual(self.engine.path("AI_Local_Engine/test.py"), self.root / "AI_Local_Engine" / "test.py")

    def test_root_link_rejected(self):
        target = self.parent / "target"
        target.mkdir()
        try:
            self.root.symlink_to(target, target_is_directory=True)
        except OSError:
            self.skipTest("Criacao de symlink sem privilegio indisponivel")
        with self.assertRaises(SafetyError):
            MasterEngine(self.root)

    def test_nested_link_rejected(self):
        self.engine.setup_structure()
        outside = self.parent / "outside"
        outside.mkdir()
        link = self.root / "link"
        try:
            link.symlink_to(outside, target_is_directory=True)
        except OSError:
            self.skipTest("Symlink indisponivel")
        with self.assertRaises(SafetyError):
            self.engine.path("link/x")

    def test_invalid_module(self):
        with self.assertRaises(ValueError):
            self.engine.install_module("99")
        self.assertFalse(self.root.exists())

    def test_all_module_aliases(self):
        for alias in ["ai", "crypto", "db", "gaming", "network"]:
            with self.subTest(alias=alias):
                self.assertEqual(self.engine.install_module(alias)["status"], "prepared")

    def test_no_implicit_subprocess(self):
        with patch("official_core.engine.subprocess.run") as runner:
            for choice in range(1, 6):
                self.engine.install_module(str(choice))
            runner.assert_not_called()

    def test_venv_only_for_ai(self):
        with self.assertRaises(ValueError):
            self.engine.install_module("db", create_venv=True)

    def test_ai_without_venv(self):
        with patch("official_core.engine.venv.EnvBuilder") as builder:
            result = self.engine.deploy_ai_engine()
            builder.assert_not_called()
        self.assertFalse(result["models_downloaded"])
        self.assertFalse((self.root / "AI_Local_Engine/ai_env").exists())

    def test_ai_generated_script_compiles(self):
        self.engine.deploy_ai_engine()
        text = (self.root / "AI_Local_Engine/run_ai_test.py").read_text()
        compile(text, "generated-ai-test", "exec")

    def test_venv_created_explicitly(self):
        def fake_create(path):
            executable = Path(path) / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
            executable.parent.mkdir(parents=True)
            executable.write_text("test")
        with patch("official_core.engine.venv.EnvBuilder") as builder:
            builder.return_value.create.side_effect = fake_create
            result = self.engine.deploy_ai_engine(create_venv=True)
            builder.assert_called_once_with(with_pip=True, clear=False, upgrade_deps=False)
            builder.return_value.create.assert_called_once()
        self.assertEqual(result["status"], "venv_ready")

    def test_incomplete_venv_not_overwritten(self):
        self.engine._mkdir("AI_Local_Engine/ai_env")
        with self.assertRaises(SafetyError):
            self.engine.deploy_ai_engine(create_venv=True)

    def test_network_disabled(self):
        self.engine.install_module("network")
        config = json.loads((self.root / "Network_Tunnels/config.json").read_text())
        self.assertFalse(config["enabled"])
        self.assertFalse(config["tunneling_implemented"])
        self.assertEqual(config["bind"], "127.0.0.1")

    def test_gaming_not_executed(self):
        self.engine.install_module("gaming")
        config = json.loads((self.root / "Gaming_Environment/session.json").read_text())
        self.assertFalse(config["automatic_execution"])
        self.assertIsNone(config["engine"])

    def test_vault_disclaimer(self):
        self.engine.install_module("crypto")
        self.assertIn("NAO E COFRE CRIPTOGRAFADO", (self.root / "Crypto_Vault/AVISO.txt").read_text())

    def test_note_roundtrip(self):
        result = self.engine.add_note("Titulo", "Anotacao")
        self.assertEqual(result["id"], 1)
        notes = self.engine.list_notes()
        self.assertEqual(notes[0]["body"], "Anotacao")

    def test_sql_injection_is_data(self):
        payload = "Robert); DROP TABLE notes;--"
        self.engine.add_note(payload)
        self.assertEqual(self.engine.list_notes()[0]["title"], payload)
        self.engine.add_note("Depois")
        self.assertEqual(len(self.engine.list_notes()), 2)

    def test_note_order_and_limit(self):
        for number in range(3):
            self.engine.add_note(str(number))
        notes = self.engine.list_notes(2)
        self.assertEqual([note["title"] for note in notes], ["2", "1"])

    def test_invalid_note_titles(self):
        for title in ["", "  ", "x" * 201, None]:
            with self.subTest(title=title), self.assertRaises(ValueError):
                self.engine.add_note(title)

    def test_invalid_note_body(self):
        with self.assertRaises(ValueError):
            self.engine.add_note("ok", "x" * 10001)

    def test_invalid_note_limits(self):
        for limit in [0, -1, 101, True, "10"]:
            with self.subTest(limit=limit), self.assertRaises(ValueError):
                self.engine.list_notes(limit)

    def test_sha256_output(self):
        path = self.parent / "sample"
        path.write_bytes(b"abc")
        result = sha256_file(path)
        self.assertEqual(result["sha256"], "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad")
        self.assertEqual(result["bytes"], 3)

    def test_hash_size_limit(self):
        path = self.parent / "sample"
        path.write_bytes(b"abc")
        with self.assertRaises(ValueError):
            sha256_file(path, max_bytes=2)

    def test_hash_missing_file(self):
        with self.assertRaises(SafetyError):
            sha256_file(self.parent / "missing")

    def test_doctor_no_gpu_tool(self):
        with patch("official_core.engine.shutil.which", return_value=None):
            result = self.engine.doctor()
        self.assertFalse(result["nvidia_smi_available"])
        self.assertEqual(result["cuda_compatibility"], "not_validated")
        self.assertFalse(self.root.exists())

    def test_gpu_uses_no_shell(self):
        with patch("official_core.engine.shutil.which", return_value="/trusted/nvidia-smi"), patch("official_core.engine.subprocess.run") as runner:
            runner.return_value.returncode = 0
            runner.return_value.stdout = "NVIDIA test"
            self.assertTrue(self.engine.check_nvidia_gpu())
            self.assertFalse(runner.call_args.kwargs["shell"])
            self.assertEqual(runner.call_args.kwargs["timeout"], 5)

    def test_gpu_timeout(self):
        with patch("official_core.engine.shutil.which", return_value="/tool"), patch("official_core.engine.subprocess.run", side_effect=subprocess.TimeoutExpired("tool", 5)):
            self.assertFalse(self.engine.check_nvidia_gpu())

    def test_cli_init(self):
        status, text, _ = self.invoke("init")
        self.assertEqual(status, 0)
        self.assertEqual(json.loads(text)["status"], "structure_ready")

    def test_cli_prepare(self):
        status, text, _ = self.invoke("prepare", "network")
        self.assertEqual(status, 0)
        self.assertFalse(json.loads(text)["network_started"])

    def test_cli_database(self):
        self.assertEqual(self.invoke("note-add", "Teste", "--body", "ok")[0], 0)
        status, text, _ = self.invoke("note-list")
        self.assertEqual(status, 0)
        self.assertEqual(json.loads(text)[0]["title"], "Teste")

    def test_cli_error_exit(self):
        status, _, errors = self.invoke("note-list", "--limit", "0")
        self.assertEqual(status, 1)
        self.assertIn("Erro:", errors)

    def test_cli_help_has_no_write(self):
        status, text, _ = self.invoke()
        self.assertEqual(status, 0)
        self.assertIn("init", text)
        self.assertFalse(self.root.exists())

    def test_menu_exit(self):
        with patch("builtins.input", return_value="0"), contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(menu(), 0)

    def test_menu_eof(self):
        with patch("builtins.input", side_effect=EOFError), contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(menu(), 0)


if __name__ == "__main__":
    unittest.main()
