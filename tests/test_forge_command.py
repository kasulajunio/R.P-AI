import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from official_core.console import main


class ForgeCommandTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name).resolve()
        self.directory = self.base / "bin"
        self.workspace = self.base / "workspace"
        self.stack = contextlib.ExitStack()
        self.addCleanup(self.stack.close)
        self.network = self.stack.enter_context(patch("official_core.forge.build_opener"))
        self.archive_network = self.stack.enter_context(patch("official_core.forge_archives.build_opener"))
        self.stack.enter_context(patch("official_core.forge.platform_key", return_value="linux-glibc-aarch64"))
        self.stack.enter_context(patch("official_core.forge_archives.platform_key", return_value="linux-glibc-aarch64"))
        self.stack.enter_context(patch("official_core.forge.shutil.which", return_value=None))

    def invoke(self, *arguments):
        stream = io.StringIO()
        with contextlib.redirect_stdout(stream), contextlib.redirect_stderr(io.StringIO()):
            code = main(["--root", str(self.workspace), "forge", *arguments, "--directory", str(self.directory)])
        return code, json.loads(stream.getvalue()) if stream.getvalue() else None

    def assert_offline(self):
        self.network.assert_not_called()
        self.archive_network.assert_not_called()
        self.assertFalse(self.directory.exists())
        self.assertFalse(self.workspace.exists())

    def test_multiple_archives_plan_through_console(self):
        code, report = self.invoke("plan", "rg", "fd")
        self.assertEqual(code, 0)
        self.assertEqual([item["tool"] for item in report["items"]], ["rg", "fd"])
        self.assert_offline()

    def test_mixed_catalog_plan(self):
        code, report = self.invoke("plan", "jq", "rg", "fd")
        self.assertEqual(code, 0)
        self.assertEqual(len(report["items"]), 3)
        self.assertEqual(report["status"], "planned")
        self.assert_offline()

    def test_single_jq_keeps_legacy_json(self):
        code, report = self.invoke("plan", "jq")
        self.assertEqual(code, 0)
        self.assertEqual(report["status"], "download_required")
        self.assertNotIn("items", report)
        self.assert_offline()

    def test_late_unknown_item_prevents_all_network(self):
        code, _ = self.invoke("install", "jq", "rg", "nmap", "--allow-network")
        self.assertEqual(code, 1)
        self.assert_offline()

    def test_missing_consent_is_usage_error(self):
        with self.assertRaises(SystemExit) as error:
            self.invoke("install", "rg", "fd")
        self.assertEqual(error.exception.code, 2)
        self.assert_offline()

    def test_duplicate_tools_fail_before_network(self):
        code, _ = self.invoke("install", "rg", "rg", "--allow-network")
        self.assertEqual(code, 1)
        self.assert_offline()

    def test_mixed_batch_abi_failure_precedes_any_download(self):
        with patch("official_core.forge_archives.platform_key", return_value="termux-aarch64"):
            code, _ = self.invoke("install", "jq", "rg", "--allow-network")
        self.assertEqual(code, 1)
        self.assert_offline()

    def test_partial_report_has_nonzero_exit(self):
        report = {"status": "partial", "items": [{"tool": "rg", "status": "installed"}], "failed_tool": "fd"}
        with patch("official_core.forge_command.execute", return_value=report):
            code, result = self.invoke("install", "rg", "fd", "--allow-network")
        self.assertEqual(code, 1)
        self.assertEqual(result, report)
        self.assert_offline()

    def test_archive_install_routes_through_verified_installer(self):
        with patch("official_core.forge_archives.install_planned", side_effect=lambda item: {**item, "status": "installed", "downloaded": True}) as installer:
            code, report = self.invoke("install", "rg", "fd", "--allow-network")
        self.assertEqual(code, 0)
        self.assertEqual(report["status"], "complete")
        self.assertEqual([c.args[0]["tool"] for c in installer.call_args_list], ["rg", "fd"])
        self.assert_offline()


if __name__ == "__main__":
    unittest.main()
