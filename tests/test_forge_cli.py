"""Integracao do comando real; downloads proibidos ou simulados."""
import contextlib
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from official_core.console import main


class ForgeCLITests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name).resolve()
        self.root = self.base / "workspace"
        self.bin = self.base / "bin"

    def cli(self, *arguments):
        return main(["--root", str(self.root), *arguments])

    def test_help_has_no_workspace_effect(self):
        with contextlib.redirect_stdout(io.StringIO()) as output, self.assertRaises(SystemExit) as result:
            self.cli("forge", "--help")
        self.assertEqual(result.exception.code, 0)
        self.assertIn("--allow-network", output.getvalue())
        self.assertFalse(self.root.exists())

    def test_plan_delegates_without_core_install_or_report(self):
        with patch("official_core.console.forge_main", return_value=0) as forge, patch("official_core.launcher.install") as install, patch("official_core.launcher.write_report") as report:
            self.assertEqual(self.cli("forge", "plan", "jq", "--directory", str(self.bin)), 0)
        forge.assert_called_once_with(["plan", "jq", "--directory", str(self.bin)])
        install.assert_not_called()
        report.assert_not_called()

    def test_install_forwards_explicit_authorization(self):
        with patch("official_core.console.forge_main", return_value=0) as forge:
            self.assertEqual(self.cli("forge", "install", "jq", "--allow-network", "--directory", str(self.bin)), 0)
        forge.assert_called_once_with(["install", "jq", "--directory", str(self.bin), "--allow-network"])
        self.assertFalse(self.root.exists())

    def test_plan_uses_real_resolver_without_network_or_writes(self):
        with patch("official_core.forge.shutil.which", return_value=None), patch("official_core.forge.platform_key", return_value="linux-glibc-x86_64"), patch("official_core.forge.build_opener") as network, contextlib.redirect_stdout(io.StringIO()) as output:
            self.assertEqual(self.cli("forge", "plan", "jq", "--directory", str(self.bin)), 0)
        payload = json.loads(output.getvalue())
        self.assertEqual(payload["status"], "download_required")
        self.assertFalse(payload["downloaded"])
        self.assertEqual(Path(payload["path"]).parent, self.bin)
        self.assertFalse(self.root.exists())
        self.assertFalse(self.bin.exists())
        network.assert_not_called()

    def test_install_without_flag_refuses_before_network(self):
        with patch("official_core.forge.build_opener") as network, contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as result:
            self.cli("forge", "install", "jq", "--directory", str(self.bin))
        self.assertEqual(result.exception.code, 2)
        self.assertFalse(self.root.exists())
        self.assertFalse(self.bin.exists())
        network.assert_not_called()

    def test_unknown_tool_is_not_searched_on_github(self):
        with patch("official_core.forge.build_opener") as network, contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(self.cli("forge", "install", "unapproved", "--allow-network", "--directory", str(self.bin)), 1)
        network.assert_not_called()
        self.assertFalse(self.bin.exists())

    def test_termux_has_no_linux_binary_fallback(self):
        with patch("official_core.forge.shutil.which", return_value=None), patch("official_core.forge.platform_key", return_value="termux-aarch64"), patch("official_core.forge.build_opener") as network, contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(self.cli("forge", "install", "jq", "--allow-network", "--directory", str(self.bin)), 1)
        network.assert_not_called()
        self.assertFalse(self.bin.exists())

    def test_raw_repository_argument_is_not_accepted(self):
        with patch("official_core.console.forge_main") as forge, contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as result:
            self.cli("forge", "install", "jq", "arbitrary/repository", "--allow-network")
        self.assertEqual(result.exception.code, 2)
        forge.assert_not_called()

    def test_real_python_entrypoint_help(self):
        source = Path(__file__).resolve().parents[1]
        result = subprocess.run([sys.executable, str(source / "rpa.py"), "--root", str(self.root), "forge", "--help"], cwd=source, capture_output=True, text=True, timeout=30, shell=False)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("--allow-network", result.stdout)
        self.assertFalse(self.root.exists())


if __name__ == "__main__":
    unittest.main()
