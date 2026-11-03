import contextlib
import io
import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from official_core.bootstrap import detect_system, install
from official_core.launcher import main, update, autoload, OFFICIAL_REMOTES
import autoload as startup


class LauncherTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name).resolve()
        self.root = self.directory / "data"

    def test_system_detection(self):
        for system, expected in [("Linux", "linux"), ("Windows", "windows"), ("Darwin", "macos"), ("Android", "android"), ("Other", "unsupported")]:
            self.assertEqual(detect_system(system, {}), expected)
        self.assertEqual(detect_system("Linux", {"TERMUX_VERSION": "test"}), "termux")

    def test_real_boot_and_reuse(self):
        first = install(self.root)
        self.assertTrue(Path(first["venv"]).is_file())
        self.assertEqual(install(self.root)["venv"], first["venv"])
        self.assertFalse(first["models_downloaded"])
        self.assertFalse(first["system_packages_installed"])

    def test_cli_reports_omit_note_text(self):
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(main(["--root", str(self.root), "install", "--no-venv"]), 0)
            self.assertEqual(main(["--root", str(self.root), "run", "note-add", "PRIVATE_TEXT_DO_NOT_LOG"]), 0)
        reports = list((self.root / "logs").glob("*.json"))
        self.assertEqual(len(reports), 2)
        for report in reports:
            value = report.read_text()
            self.assertNotIn("PRIVATE_TEXT_DO_NOT_LOG", value)
            self.assertTrue(json.loads(value)["success"])

    def repo(self):
        source = self.directory / "repo"
        (source / ".git").mkdir(parents=True)
        return source

    def test_update_rejects_dirty_worktree(self):
        source = self.repo()
        with patch("official_core.launcher._git", side_effect=[str(source), " M file"]) as call:
            with self.assertRaises(ValueError):
                update(source)
            self.assertEqual(call.call_count, 2)

    def test_update_rejects_foreign_remote(self):
        source = self.repo()
        with patch("official_core.launcher._git", side_effect=[str(source), "", "main", "https://example.invalid/repo"]) as call:
            with self.assertRaises(ValueError):
                update(source)
            self.assertEqual(call.call_count, 4)

    def test_update_only_fast_forward(self):
        source = self.repo()
        with patch("official_core.launcher._git", side_effect=[str(source), "", "main", sorted(OFFICIAL_REMOTES)[0], "", "abc123"]) as call:
            self.assertEqual(update(source)["commit"], "abc123")
            self.assertEqual(call.call_args_list[4].args[1:], ("pull", "--ff-only", "origin", "main"))

    def test_autoload_is_not_activated_and_no_overwrite(self):
        for target in ("linux", "windows", "termux"):
            result = autoload(self.root, self.directory, target)
            self.assertFalse(result["activated"])
            content = Path(result["path"]).read_text()
            self.assertNotIn("--auto-update", content)
            with self.assertRaises(FileExistsError):
                autoload(self.root, self.directory, target)

    def test_failure_generates_report(self):
        with patch("official_core.launcher.install", side_effect=RuntimeError("synthetic failure")), contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(main(["--root", str(self.root), "install"]), 1)
        report = json.loads(next((self.root / "logs").glob("*.json")).read_text())
        self.assertFalse(report["success"])
        self.assertEqual(report["error_type"], "RuntimeError")

    def test_startup_no_implicit_update(self):
        with patch("autoload.rpa", return_value=0) as call:
            self.assertEqual(startup.main(["--root", str(self.root), "--no-venv"]), 0)
            self.assertEqual(call.call_count, 2)
            self.assertFalse(any("update" in value.args[0] for value in call.call_args_list))

    def test_startup_stops_after_update_error(self):
        with patch("autoload.rpa", return_value=1) as call:
            self.assertEqual(startup.main(["--auto-update"]), 1)
            self.assertEqual(call.call_count, 1)


if __name__ == "__main__":
    unittest.main()
