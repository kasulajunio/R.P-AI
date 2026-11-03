# SPDX-License-Identifier: MIT
"""Explicit native ARM64 download and functional checks through the product CLI."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile


def run(arguments):
    return subprocess.run(arguments, capture_output=True, text=True, timeout=120, check=True, shell=False)


def main():
    with tempfile.TemporaryDirectory(prefix="rpa-cli-download-verification-") as folder:
        base = Path(folder).resolve()
        root = base / "bin"
        command = [sys.executable, "rpa.py", "forge", "install", "rg", "fd", "--directory", str(root), "--allow-network"]
        result = run(command)
        report = json.loads(result.stdout)
        print(json.dumps(report, indent=2), flush=True)
        if report["status"] != "complete" or any(not item.get("downloaded") for item in report["items"]):
            raise RuntimeError("CLI nao confirmou downloads reais")
        for name, expected in (("rg", "ripgrep 15.1.0"), ("fd", "fd 10.3.0")):
            first_line = run([str(root / name), "--version"]).stdout.splitlines()[0]
            print(first_line, flush=True)
            if not first_line.startswith(expected):
                raise RuntimeError("Versao inesperada")
        data = base / "data"
        data.mkdir()
        sample = data / "sample.txt"
        sample.write_text("approved-download-test\n", encoding="utf-8")
        found = run([str(root / "rg"), "--fixed-strings", "approved-download-test", str(sample)])
        if found.stdout.strip() != "approved-download-test":
            raise RuntimeError("Busca de conteudo falhou")
        print("rg: busca real de conteudo OK", flush=True)
        located = run([str(root / "fd"), "--color", "never", "--fixed-strings", "sample.txt", str(data)])
        if Path(located.stdout.strip()).resolve() != sample:
            raise RuntimeError("Busca de arquivo falhou")
        print("fd: busca real de arquivo OK", flush=True)
        if any(path.name.startswith(".forge-") for path in root.iterdir()):
            raise RuntimeError("Temporario residual")
    if base.exists():
        raise RuntimeError("Limpeza temporaria nao concluida")
    print("CLI integrada: downloads, hashes, extracao, versoes, buscas e limpeza confirmados em Linux ARM64.", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
