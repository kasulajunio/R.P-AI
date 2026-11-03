# SPDX-License-Identifier: MIT
"""Opt-in archive installation for two pinned Linux ARM64/glibc assets."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import sys
import tarfile
import tempfile
from urllib.request import Request, build_opener
from .forge import Asset, ApprovedRedirect, check_path, check_url, platform_key

PLATFORM = "linux-glibc-aarch64"
MAX_BINARY = 64 * 1024 * 1024
MAX_EXPANDED = 128 * 1024 * 1024
CATALOG = {
    "rg": (Asset("https://github.com/BurntSushi/ripgrep/releases/download/15.1.0/ripgrep-15.1.0-aarch64-unknown-linux-gnu.tar.gz", "2b661c6ef508e902f388e9098d9c4c5aca72c87b55922d94abdba830b4dc885e", "15.1.0"), 1869959, "ripgrep-15.1.0-aarch64-unknown-linux-gnu/rg"),
    "fd": (Asset("https://github.com/sharkdp/fd/releases/download/v10.3.0/fd-v10.3.0-aarch64-unknown-linux-gnu.tar.gz", "66f297e404400a3358e9a0c0b2f3f4725956e7e4435427a9ae56e22adbe73a68", "v10.3.0"), 1575492, "fd-v10.3.0-aarch64-unknown-linux-gnu/fd"),
}


def plan(tool, directory=None):
    if not isinstance(tool, str) or tool not in CATALOG:
        raise ValueError("Ferramenta fora do catalogo de arquivos")
    if platform_key() != PLATFORM:
        raise ValueError("Exige Linux ARM64/glibc; sem fallback Android, Termux ou outra ABI")
    root = Path(os.path.abspath(os.path.expanduser(str(directory or Path.home() / ".rpa" / "bin"))))
    target = root / tool
    check_path(target)
    if target.exists():
        raise FileExistsError("Destino existente; nao sobrescrito nem reutilizado sem verificacao")
    asset, size, member = CATALOG[tool]
    asset.validate()
    return {"tool": tool, "path": str(target), "platform": PLATFORM, "version": asset.version,
            "url": asset.url, "sha256": asset.sha256, "size": size, "member": member,
            "status": "download_required", "downloaded": False}


def copy_selected(package, destination, expected):
    """Validate every member, then copy one exact regular file, never extractall."""
    selected = None
    seen = set()
    expanded = 0
    root = expected.split("/")[0]
    with tarfile.open(package, "r:gz") as archive:
        for count, member in enumerate(archive, 1):
            name = member.name.rstrip("/")
            parts = name.split("/")
            if (count > 4096 or not name or name.startswith("/") or "\\" in name
                    or any(part in ("", ".", "..") for part in parts) or parts[0] != root
                    or name in seen or not (member.isdir() or member.isfile())
                    or getattr(member, "sparse", None) is not None):
                raise ValueError("Membro de arquivo nao permitido")
            seen.add(name)
            expanded += member.size
            if expanded > MAX_EXPANDED or member.size < 0:
                raise ValueError("Arquivo expandido excede limite")
            if name == expected:
                if not member.isfile() or not 0 < member.size <= MAX_BINARY:
                    raise ValueError("Executavel esperado invalido")
                selected = member
        if selected is None:
            raise ValueError("Executavel exato nao encontrado")
        with archive.extractfile(selected) as source, destination.open("xb") as output:
            total = 0
            while True:
                block = source.read(65536)
                if not block:
                    break
                total += len(block)
                if total > MAX_BINARY or total > selected.size:
                    raise ValueError("Executavel excede tamanho declarado")
                output.write(block)
            if total != selected.size:
                raise ValueError("Executavel truncado")
            output.flush()
            os.fsync(output.fileno())
    with destination.open("rb") as binary:
        header = binary.read(64)
    if len(header) < 64 or header[:6] != b"\x7fELF\x02\x01" or int.from_bytes(header[18:20], "little") != 183:
        raise ValueError("Exige ELF64 little-endian AArch64")


def install_planned(item):
    target = Path(item["path"])
    root = target.parent
    check_path(target)
    if target.exists():
        raise FileExistsError("Destino apareceu; nao sobrescrito")
    root.mkdir(parents=True, exist_ok=True, mode=0o700)
    check_path(root)
    if root.stat().st_mode & 0o022:
        raise PermissionError("Pasta permite escrita por grupo ou outros")
    with tempfile.TemporaryDirectory(prefix=".forge-archive-", dir=root) as staging:
        package = Path(staging) / "package.tar.gz"
        binary = Path(staging) / "binary"
        digest = hashlib.sha256()
        total = 0
        check_url(item["url"], initial=True)
        request = Request(item["url"], headers={"User-Agent": "RP-AI-Forge-Archives/1", "Accept": "application/octet-stream"})
        with build_opener(ApprovedRedirect()).open(request, timeout=30) as response, package.open("xb") as output:
            check_url(response.geturl())
            if response.status != 200:
                raise OSError("Status HTTP inesperado")
            while True:
                block = response.read(65536)
                if not block:
                    break
                total += len(block)
                if total > item["size"]:
                    raise ValueError("Pacote excede tamanho aprovado")
                digest.update(block)
                output.write(block)
        if total != item["size"] or digest.hexdigest() != item["sha256"]:
            raise ValueError("Tamanho ou SHA-256 divergente")
        copy_selected(package, binary, item["member"])
        os.chmod(binary, 0o700)
        check_path(target)
        os.link(binary, target)
    return {**item, "status": "installed", "downloaded": True}


def batch(tools, directory=None, *, install=False, allow_network=False):
    if not isinstance(tools, (list, tuple)) or not tools or len(tools) > 2 or any(not isinstance(t, str) for t in tools) or len(set(tools)) != len(tools):
        raise ValueError("Informe rg e/ou fd, sem duplicatas")
    if install and not allow_network:
        raise PermissionError("install exige --allow-network")
    plans = [plan(tool, directory) for tool in tools]
    if not install:
        return {"status": "planned", "items": plans}
    completed = []
    for index, item in enumerate(plans):
        try:
            completed.append(install_planned(item))
        except (OSError, ValueError, RuntimeError, tarfile.TarError, EOFError) as error:
            return {"status": "partial" if completed else "failed", "items": completed,
                    "failed_tool": item["tool"], "error_type": type(error).__name__,
                    "not_attempted": list(tools[index + 1:])}
    return {"status": "complete", "items": completed}


def main(argv=None):
    parser = argparse.ArgumentParser(description="Arquivos aprovados rg/fd, sem extracao generica")
    parser.add_argument("action", choices=["plan", "install"])
    parser.add_argument("tools", nargs="+", choices=sorted(CATALOG))
    parser.add_argument("--directory")
    parser.add_argument("--allow-network", action="store_true")
    args = parser.parse_args(argv)
    if args.action == "install" and not args.allow_network:
        parser.error("install exige --allow-network")
    try:
        report = batch(args.tools, args.directory, install=args.action == "install", allow_network=args.allow_network)
    except (OSError, ValueError, RuntimeError) as error:
        print("Arquivos bloqueados: " + type(error).__name__, file=sys.stderr)
        return 1
    print(json.dumps(report, indent=2))
    return 0 if report["status"] in ("planned", "complete") else 1


if __name__ == "__main__":
    raise SystemExit(main())
