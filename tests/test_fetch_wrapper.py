import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
WRAPPER = ROOT / "scripts" / "fetch"
BASH = shutil.which("bash")

@unittest.skipIf(os.name == "nt" or BASH is None, "POSIX Bash wrapper; Python CLI tested separately")
class FetchWrapperTests(unittest.TestCase):
    def invoke(self, wrapper, args, cwd, env=None):
        return subprocess.run([BASH, str(wrapper), *args], cwd=cwd, env=env, capture_output=True, text=True, timeout=30, check=False)

    def fixture(self, folder, exit_code=0):
        project = Path(folder) / "project with spaces"
        (project / "scripts").mkdir(parents=True)
        wrapper = project / "scripts" / "fetch"
        shutil.copyfile(WRAPPER, wrapper)
        source = "import json, sys\nprint(json.dumps(sys.argv[1:]))\n" + f"raise SystemExit({exit_code})\n"
        (project / "rpa.py").write_text(source, encoding="utf-8")
        return wrapper

    def test_bash_syntax(self):
        result = subprocess.run([BASH, "-n", str(WRAPPER)], capture_output=True, text=True, timeout=10, check=False)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_arguments_paths_and_no_shell_evaluation(self):
        with tempfile.TemporaryDirectory() as folder:
            wrapper = self.fixture(folder)
            args = ["plan", "jq", "--directory", "space dir; touch UNEXPECTED"]
            result = self.invoke(wrapper, args, folder)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(result.stdout), ["forge", *args])
            self.assertFalse((Path(folder) / "UNEXPECTED").exists())

    def test_failure_code_preserved(self):
        with tempfile.TemporaryDirectory() as folder:
            result = self.invoke(self.fixture(folder, 27), ["plan", "jq"], folder)
            self.assertEqual(result.returncode, 27, result.stderr)
            self.assertNotIn("SUCESSO", result.stdout)

    def test_no_arguments_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            result = self.invoke(WRAPPER, [], folder)
            self.assertEqual(result.returncode, 2, result.stderr)
            self.assertIn("Uso:", result.stderr)

    def test_install_without_consent_rejected_before_writing(self):
        with tempfile.TemporaryDirectory() as folder:
            destination = Path(folder) / "private-bin"
            env = dict(os.environ, HOME=folder, PYTHONDONTWRITEBYTECODE="1")
            result = self.invoke(WRAPPER, ["install", "jq", "--directory", str(destination)], folder, env)
            self.assertEqual(result.returncode, 2, result.stderr)
            self.assertIn("--allow-network", result.stderr)
            self.assertFalse(destination.exists())

if __name__ == "__main__":
    unittest.main()
