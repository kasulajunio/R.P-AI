import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from official_core.bootstrap import install


class EntryPointTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve() / "workspace"
        self.source = Path(__file__).resolve().parents[1]

    def execute(self, file, *arguments):
        return subprocess.run([sys.executable, str(self.source / file), *arguments], cwd=str(self.source), capture_output=True, text=True, timeout=30, shell=False)

    def test_boot_without_pip(self):
        result = self.execute("boot.py", "--root", str(self.root), "--no-venv")
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        # boot.py chama bootstrap completo; install isolado retorna core_ready.
        self.assertEqual(payload["status"], "boot_complete")
        self.assertFalse(payload["inference_implemented"])
        self.assertIn("MIT", result.stderr)
        self.assertEqual(len(list((self.root / "logs").glob("*.json"))), 1)
        self.assertTrue(Path(payload["report"]).is_file())

    def test_new_cli_real_data(self):
        result = self.execute("rpa.py", "--root", str(self.root), "run", "note-add", "Synthetic example")
        self.assertEqual(result.returncode, 0, result.stderr)
        result = self.execute("rpa.py", "--root", str(self.root), "run", "note-list")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)[0]["title"], "Synthetic example")

    def test_autoload_real_offline(self):
        result = self.execute("autoload.py", "--root", str(self.root), "--no-venv")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((self.root / "Database_Nexus" / "notes.sqlite3").is_file())
        self.assertEqual(len(list((self.root / "logs").glob("*.json"))), 2)

    def test_partial_venv_is_not_overwritten(self):
        directory = self.root / "AI_Local_Engine" / "ai_env"
        directory.mkdir(parents=True)
        marker = directory / "keep.txt"
        marker.write_text("preserve")
        with self.assertRaises(RuntimeError):
            install(self.root)
        self.assertEqual(marker.read_text(), "preserve")


if __name__ == "__main__":
    unittest.main()
