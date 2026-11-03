import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from official_core.bootstrap import install
from official_core.console import main, status, VERSION


class ConsoleTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name).resolve()
        self.root = self.base / "workspace"

    def test_status_does_not_initialize_database(self):
        result = status(self.root, self.base)
        self.assertEqual(result["database"]["state"], "not_initialized")
        self.assertFalse(self.root.exists())
        self.assertTrue(result["inference_implemented"])
        self.assertEqual(result["model_availability"], "not_checked")
        self.assertFalse(result["model_installed_by_rpa"])
        self.assertFalse(result["background_service_started"])

    def test_status_after_install(self):
        install(self.root, create_venv=False)
        result = status(self.root, self.base)
        self.assertTrue(result["configured"])
        self.assertTrue(result["database"]["ok"])
        self.assertFalse(result["venv_python_exists"])

    def test_status_reports_corruption(self):
        install(self.root, create_venv=False)
        database = self.root / "Database_Nexus" / "notes.sqlite3"
        database.write_bytes(b"Not a SQLite database")
        result = status(self.root, self.base)
        self.assertFalse(result["database"]["ok"])
        self.assertEqual(database.read_bytes(), b"Not a SQLite database")
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(main(["--root", str(self.root), "--source", str(self.base), "status"]), 1)

    def test_cli_status_logs_no_note_content(self):
        with contextlib.redirect_stdout(io.StringIO()) as output:
            code = main(["--root", str(self.root), "--source", str(self.base), "status"])
        self.assertEqual(code, 0)
        result = json.loads(output.getvalue())
        report = json.loads(Path(result["report"]).read_text())
        self.assertTrue(report["success"])
        self.assertEqual(report["command"], "status")
        self.assertFalse((self.root / "Database_Nexus" / "notes.sqlite3").exists())

    def test_install_and_run_remain_real(self):
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(main(["--root", str(self.root), "install", "--no-venv"]), 0)
            self.assertEqual(main(["--root", str(self.root), "run", "note-add", "Teste funcional"]), 0)
            self.assertEqual(main(["--root", str(self.root), "run", "note-get", "99999"]), 1)

    def test_nested_root_rejected(self):
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(main(["--root", str(self.root), "run", "--root=other", "doctor"]), 1)

    def test_version_has_no_workspace_side_effect(self):
        with contextlib.redirect_stdout(io.StringIO()) as output, self.assertRaises(SystemExit) as error:
            main(["--root", str(self.root), "--version"])
        self.assertEqual(error.exception.code, 0)
        self.assertIn(VERSION, output.getvalue())
        self.assertFalse(self.root.exists())


if __name__ == "__main__":
    unittest.main()
