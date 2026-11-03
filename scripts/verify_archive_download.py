# SPDX-License-Identifier: MIT
"""One explicit native ARM64 smoke test, no persistent device installation."""
import json
from pathlib import Path
import subprocess
import tempfile
from official_core.forge_archives import batch


def main():
    with tempfile.TemporaryDirectory(prefix="rpa-archive-verification-") as folder:
        root = Path(folder).resolve() / "bin"
        report = batch(["rg", "fd"], str(root), install=True, allow_network=True)
        print(json.dumps(report, indent=2), flush=True)
        if report["status"] != "complete":
            return 1
        for name, expected in (("rg", "ripgrep 15.1.0"), ("fd", "fd 10.3.0")):
            result = subprocess.run([str(root / name), "--version"], capture_output=True, text=True, timeout=15, check=True, shell=False)
            first_line = result.stdout.splitlines()[0]
            print(first_line, flush=True)
            if not first_line.startswith(expected):
                raise RuntimeError("Versao inesperada")
    print("Downloads, hashes, extracao, execucao ARM64 e limpeza temporaria confirmados.", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
