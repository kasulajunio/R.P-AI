"""Teste real, offline, em processos separados e workspace descartavel."""
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(arguments):
    result = subprocess.run(arguments, cwd=str(ROOT), capture_output=True, text=True, encoding="utf-8", timeout=120, shell=False)
    if result.returncode != 0:
        raise RuntimeError(result.stdout + result.stderr)
    return result.stdout


def main():
    completed = []
    with tempfile.TemporaryDirectory(prefix="rp-ai-smoke-") as temporary:
        workspace = Path(temporary).resolve() / "workspace"
        command = [sys.executable, "-m", "official_core", "--root", str(workspace)]

        def cli(*args):
            return json.loads(run(command + list(args)))

        assert cli("init")["status"] == "structure_ready"
        before = (workspace / "core.json").read_bytes()
        cli("init")
        assert (workspace / "core.json").read_bytes() == before
        completed.append("init_idempotent")
        for module in ["ai", "crypto", "db", "gaming", "network"]:
            assert cli("prepare", module)["status"] == "prepared"
        completed.append("five_modules_prepared")
        prepared = cli("prepare", "ai", "--venv")
        assert prepared["status"] == "venv_ready"
        python = prepared["python"]
        probe = run([python, "-c", "import json,sys; print(json.dumps({\"isolated\": sys.prefix != sys.base_prefix}))"])
        assert json.loads(probe)["isolated"] is True
        output = run([python, str(workspace / "AI_Local_Engine/run_ai_test.py")])
        assert "PyTorch nao instalado" in output
        assert cli("prepare", "ai", "--venv")["status"] == "venv_ready"
        completed.append("real_venv_created_executed_reused")
        assert cli("note-add", "Persistencia", "--body", "texto sintetico")["id"] == 1
        notes = cli("note-list")
        assert len(notes) == 1 and notes[0]["body"] == "texto sintetico"
        completed.append("sqlite_persists_across_processes")
        expected = hashlib.sha256((ROOT / "README.md").read_bytes()).hexdigest()
        assert cli("sha256", str(ROOT / "README.md"))["sha256"] == expected
        completed.append("hash_matches_file")
        assert cli("doctor")["cuda_compatibility"] == "not_validated"
        network = json.loads((workspace / "Network_Tunnels/config.json").read_text())
        assert network["enabled"] is False and network["tunneling_implemented"] is False
        completed.append("network_stays_disabled")
    print(json.dumps({"status": "passed", "checks": completed}, indent=2))


if __name__ == "__main__":
    main()
