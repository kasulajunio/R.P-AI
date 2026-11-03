import contextlib
import io
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from official_core.bootstrap import bootstrap, detect_system, main
from official_core.engine import MasterEngine


class BootstrapTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name).resolve() / "workspace"

    def test_platforms(self):
        for system, expected in [("Linux", "linux"), ("Windows", "windows"), ("Darwin", "macos"), ("Android", "android")]:
            with self.subTest(system=system):
                self.assertEqual(detect_system(system, {}), expected)

    def test_termux(self):
        self.assertEqual(detect_system("Linux", {"PREFIX": "/data/data/com.termux/files/usr"}), "termux")
        self.assertEqual(detect_system("Linux", {"TERMUX_VERSION": "test"}), "termux")

    def test_native_android(self):
        self.assertEqual(detect_system("Linux", {"ANDROID_ROOT": "/system"}), "android")

    def test_unknown_is_not_android(self):
        with self.assertRaises(RuntimeError):
            detect_system("UnknownOS", {})

    def test_no_environment_dump(self):
        self.assertEqual(detect_system("Linux", {"UNRELATED_SECRET": "com.termux"}), "linux")

    def test_offline_boot_is_repeatable(self):
        with patch.object(MasterEngine, "check_nvidia_gpu", return_value=False):
            first = bootstrap(self.root, create_venv=False)
            MasterEngine(self.root).add_note("Preservar", "Dados")
            second = bootstrap(self.root, create_venv=False)
        self.assertEqual(first["status"], "boot_complete")
        self.assertFalse(second["models_downloaded"])
        self.assertFalse(second["global_packages_installed"])
        self.assertEqual(len(MasterEngine(self.root).list_notes()), 1)

    def test_real_venv(self):
        with patch.object(MasterEngine, "check_nvidia_gpu", return_value=False):
            first = bootstrap(self.root)
            second = bootstrap(self.root)
        self.assertTrue(Path(first["ai_environment"]["python"]).is_file())
        self.assertEqual(second["ai_environment"]["status"], "venv_ready")
        self.assertFalse(second["inference_implemented"])

    def test_incomplete_venv_does_not_claim_success(self):
        target = self.root / "AI_Local_Engine" / "ai_env"
        target.mkdir(parents=True)
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()) as errors:
            result = main(["--root", str(self.root)])
        self.assertEqual(result, 1)
        self.assertIn("Boot falhou", errors.getvalue())

    def test_no_fake_consent(self):
        with contextlib.redirect_stdout(io.StringIO()) as output, patch.object(MasterEngine, "check_nvidia_gpu", return_value=False):
            result = main(["--root", str(self.root), "--without-venv"])
        self.assertEqual(result, 0)
        self.assertNotIn("Termos aceitos automaticamente", output.getvalue())

    def test_run_command(self):
        with contextlib.redirect_stdout(io.StringIO()), patch.object(MasterEngine, "check_nvidia_gpu", return_value=False):
            result = main(["--root", str(self.root), "--without-venv", "--run", "note-add", "Boot integrado"])
        self.assertEqual(result, 0)
        self.assertEqual(MasterEngine(self.root).list_notes()[0]["title"], "Boot integrado")

    def test_failure_is_nonzero(self):
        with patch("official_core.bootstrap.bootstrap", side_effect=subprocess.TimeoutExpired("python", 30)), contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(main(["--root", str(self.root)]), 1)


if __name__ == "__main__":
    unittest.main()
