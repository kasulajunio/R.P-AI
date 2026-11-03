import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import call, patch
from official_core.forge_batch import execute_batch, main


class ForgeBatchTests(unittest.TestCase):
    def test_invalid_lists_rejected(self):
        for tools in ([], "jq", ["jq", "jq"], [None], ["jq"] * 33):
            with self.subTest(tools=tools), self.assertRaises(ValueError):
                execute_batch(tools)

    def test_consent_required_before_resolver(self):
        with patch("official_core.forge_batch.Forge") as factory, self.assertRaises(PermissionError):
            execute_batch(["jq"], install=True)
        factory.assert_not_called()

    def test_real_plan_is_offline_and_read_only(self):
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder).resolve() / "private-bin"
            with patch("official_core.forge.shutil.which", return_value=None), patch("official_core.forge.platform_key", return_value="linux-glibc-x86_64"), patch("official_core.forge.build_opener") as network:
                report = execute_batch(["jq"], directory=str(target))
            self.assertEqual(report["status"], "planned")
            self.assertEqual(report["items"][0]["status"], "download_required")
            network.assert_not_called()
            self.assertFalse(target.exists())

    def test_unapproved_second_item_prevents_all_downloads(self):
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder).resolve() / "private-bin"
            with patch("official_core.forge.shutil.which", return_value=None), patch("official_core.forge.platform_key", return_value="linux-glibc-x86_64"), patch("official_core.forge.build_opener") as network:
                with self.assertRaises(ValueError):
                    execute_batch(["jq", "nmap"], install=True, allow_network=True, directory=str(target))
            network.assert_not_called()
            self.assertFalse(target.exists())

    def test_partial_failure_stops_and_preserves_successful_items(self):
        with patch("official_core.forge_batch.Forge") as factory:
            engine = factory.return_value
            engine.ensure.side_effect = [
                {"status": "download_required"}, {"status": "download_required"}, {"status": "download_required"},
                {"status": "installed", "downloaded": True}, OSError("synthetic failure")]
            report = execute_batch(["one", "two", "three"], install=True, allow_network=True)
            self.assertEqual(engine.ensure.call_args_list, [call("one", install=False), call("two", install=False), call("three", install=False), call("one", install=True), call("two", install=True)])
        self.assertEqual(report["status"], "partial")
        self.assertEqual(report["failed_tool"], "two")
        self.assertEqual(report["not_attempted"], ["three"])
        self.assertEqual(report["items"][0]["tool"], "one")
        self.assertNotIn("synthetic failure", json.dumps(report))

    def test_cli_requires_consent(self):
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as result:
            main(["install", "jq"])
        self.assertEqual(result.exception.code, 2)

    def test_cli_reports_failed_install_as_nonzero(self):
        with patch("official_core.forge_batch.execute_batch", return_value={"status": "failed"}), contextlib.redirect_stdout(io.StringIO()) as output:
            result = main(["install", "jq", "--allow-network"])
        self.assertEqual(result, 1)
        self.assertEqual(json.loads(output.getvalue())["status"], "failed")

    def test_complete_install_keeps_resolver_status(self):
        with patch("official_core.forge_batch.Forge") as factory:
            factory.return_value.ensure.side_effect = [{"status": "system_available"}, {"status": "system_available", "downloaded": False}]
            report = execute_batch(["jq"], install=True, allow_network=True)
        self.assertEqual(report["status"], "complete")
        self.assertFalse(report["items"][0]["downloaded"])


if __name__ == "__main__":
    unittest.main()
