# SPDX-License-Identifier: MIT
"""Opt-in real downloads and functional tests on the runner native OS/ABI."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from official_core.forge import platform_key


def run(arguments):
    return subprocess.run(arguments, capture_output=True, text=True, timeout=120, check=True, shell=False)


def main():
    key = platform_key()
    print("Native verification: " + key, flush=True)
    with tempfile.TemporaryDirectory(prefix="rpa-cli-download-verification-") as folder:
        base = Path(folder).resolve()
        root = base / "bin"
        command = [sys.executable, "rpa.py", "forge", "install", "rg", "fd", "--directory", str(root), "--allow-network"]
        result = run(command)
        report = json.loads(result.stdout)
        print(json.dumps(report, indent=2), flush=True)
        if report["status"] != "complete" or any(not item.get("downloaded") for item in report["items"]):
            raise RuntimeError("CLI nao confirmou downloads reais")
        binaries = {name: str(root / (name + (".exe" if os.name == "nt" else ""))) for name in ("rg", "fd")}
        for name, expected in (("rg", "ripgrep 15.1.0"), ("fd", "fd 10.3.0")):
            first_line = run([binaries[name], "--version"]).stdout.splitlines()[0]
            print(first_line, flush=True)
            if not first_line.startswith(expected):
                raise RuntimeError("Versao inesperada")
        data = base / "data"
        data.mkdir()
        sample = data / "sample.txt"
        sample.write_text("approved-download-test\n", encoding="utf-8")
        found = run([binaries["rg"], "--fixed-strings", "approved-download-test", str(sample)])
        if found.stdout.strip() != "approved-download-test":
            raise RuntimeError("Busca de conteudo falhou")
        print("rg: busca real de conteudo OK", flush=True)
        located = run([binaries["fd"], "--color", "never", "--fixed-strings", "sample.txt", str(data)])
        if Path(located.stdout.strip()).resolve() != sample:
            raise RuntimeError("Busca de arquivo falhou")
        print("fd: busca real de arquivo OK", flush=True)
        if any(path.name.startswith(".forge-") for path in root.iterdir()):
            raise RuntimeError("Temporario residual")
    if base.exists():
        raise RuntimeError("Limpeza temporaria nao concluida")
    print("CLI: downloads, hashes, extracao, versoes, buscas e limpeza confirmados em " + key, flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
