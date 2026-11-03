# SPDX-License-Identifier: MIT
"""Explicit approved tar.gz/ZIP installation, with native ABI checks."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import stat
import sys
import tarfile
import tempfile
import zipfile
from urllib.request import Request, build_opener
from .forge import ApprovedRedirect, check_path, check_url, platform_key
from .forge_catalog import CATALOG as PLATFORM_CATALOG

PLATFORM = "linux-glibc-aarch64"
MAX_BINARY = 64 * 1024 * 1024
MAX_EXPANDED = 128 * 1024 * 1024
CATALOG = {tool: versions[PLATFORM] for tool, versions in PLATFORM_CATALOG.items()}


def plan(tool, directory=None):
    if not isinstance(tool, str) or tool not in CATALOG:
        raise ValueError("Ferramenta fora do catalogo de arquivos")
    key = platform_key()
    root = Path(os.path.abspath(os.path.expanduser(str(directory or Path.home() / ".rpa" / "bin"))))
    target = root / (tool + (".exe" if key.startswith("windows-") else ""))
    check_path(target)
    if target.exists():
        raise FileExistsError("Destino existente; nao sobrescrito nem reutilizado sem verificacao")
    if key.startswith(("termux-", "android-")):
        found = shutil.which(tool)
        if found and Path(os.path.abspath(found)) != target:
            return {"tool": tool, "path": found, "platform": key, "status": "system_available", "downloaded": False, "directory": str(root)}
        raise ValueError("Android/Termux exige ferramenta nativa ja instalada; sem download Linux ou APK")
    selection = CATALOG[tool] if key == PLATFORM else PLATFORM_CATALOG[tool].get(key)
    if selection is None:
        raise ValueError("Sem asset aprovado para " + key + "; sem fallback de ABI")
    asset, size, member = selection
    asset.validate()
    return {"tool": tool, "path": str(target), "platform": key, "version": asset.version,
            "url": asset.url, "sha256": asset.sha256, "size": size, "member": member,
            "format": "zip" if asset.url.endswith(".zip") else "tar.gz",
            "status": "download_required", "downloaded": False}


def check_binary(path, key):
    with path.open("rb") as binary:
        header = binary.read(64)
        arch = key.rsplit("-", 1)[-1]
        if arch not in ("aarch64", "x86_64"):
            raise ValueError("Arquitetura nao aprovada")
        if key.startswith("windows-"):
            if len(header) != 64 or header[:2] != b"MZ":
                raise ValueError("Exige executavel PE")
            offset = int.from_bytes(header[60:64], "little")
            if not 64 <= offset <= min(MAX_BINARY - 6, path.stat().st_size - 6):
                raise ValueError("Cabecalho PE invalido")
            binary.seek(offset)
            coff = binary.read(6)
            machine = 0xAA64 if arch == "aarch64" else 0x8664
            if coff[:4] != b"PE\0\0" or int.from_bytes(coff[4:6], "little") != machine:
                raise ValueError("Arquitetura PE divergente")
        elif key.startswith("darwin-"):
            cpu = 0x100000C if arch == "aarch64" else 0x1000007
            if len(header) < 32 or header[:4] != b"\xcf\xfa\xed\xfe" or int.from_bytes(header[4:8], "little") != cpu:
                raise ValueError("Exige Mach-O64 da arquitetura aprovada")
        elif key.startswith(("linux-glibc-", "linux-musl-")):
            machine = 183 if arch == "aarch64" else 62
            if len(header) < 64 or header[:6] != b"\x7fELF\x02\x01" or int.from_bytes(header[18:20], "little") != machine:
                raise ValueError("Exige ELF64 little-endian da arquitetura aprovada")
        else:
            raise ValueError("Sistema nao aprovado para downloads")


def copy_selected(package, destination, expected, key=PLATFORM, archive_format="tar.gz"):
    """Inspect every member; copy only one exact regular binary, never extractall."""
    selected = None
    seen = set()
    expanded = 0
    root = expected.split("/")[0]
    if archive_format not in ("tar.gz", "zip"):
        raise ValueError("Formato nao aprovado")
    archive = zipfile.ZipFile(package) if archive_format == "zip" else tarfile.open(package, "r:gz")
    with archive:
        members = archive.infolist() if archive_format == "zip" else archive
        for count, member in enumerate(members, 1):
            is_zip = archive_format == "zip"
            original = member.orig_filename if is_zip else member.name
            name = original.rstrip("/")
            parts = name.split("/")
            directory = member.is_dir() if is_zip else member.isdir()
            size = member.file_size if is_zip else member.size
            regular = not directory if is_zip else member.isfile()
            if is_zip:
                mode = stat.S_IFMT(member.external_attr >> 16)
                safe_type = mode in (0, stat.S_IFREG, stat.S_IFDIR)
                safe_type = safe_type and not (member.flag_bits & 1)
            else:
                safe_type = (directory or regular) and getattr(member, "sparse", None) is None
            if (count > 4096 or not name or name.startswith("/") or "\\" in name or ":" in name
                    or any(ord(c) < 32 for c in original)
                    or any(part in ("", ".", "..") for part in parts) or parts[0] != root
                    or name in seen or not safe_type):
                raise ValueError("Membro de arquivo nao permitido")
            seen.add(name)
            expanded += size
            if expanded > MAX_EXPANDED or size < 0:
                raise ValueError("Arquivo expandido excede limite")
            if name == expected:
                if not regular or not 0 < size <= MAX_BINARY:
                    raise ValueError("Executavel esperado invalido")
                selected = member
        if selected is None:
            raise ValueError("Executavel exato nao encontrado")
        declared = selected.file_size if archive_format == "zip" else selected.size
        source = archive.open(selected) if archive_format == "zip" else archive.extractfile(selected)
        with source, destination.open("xb") as output:
            total = 0
            while True:
                block = source.read(65536)
                if not block:
                    break
                total += len(block)
                if total > MAX_BINARY or total > declared:
                    raise ValueError("Executavel excede tamanho declarado")
                output.write(block)
            if total != declared:
                raise ValueError("Executavel truncado")
            output.flush()
            os.fsync(output.fileno())
    check_binary(destination, key)


def install_planned(item):
    target = Path(item["path"])
    # Re-resolve the fixed catalog before network; a modified plan is not authority.
    if item != plan(item["tool"], item.get("directory", target.parent)):
        raise ValueError("Plano alterado ou sistema divergente")
    if item["status"] == "system_available":
        return item
    root = target.parent
    check_path(target)
    if target.exists():
        raise FileExistsError("Destino apareceu; nao sobrescrito")
    root.mkdir(parents=True, exist_ok=True, mode=0o700)
    check_path(root)
    if os.name != "nt" and root.stat().st_mode & 0o022:
        raise PermissionError("Pasta permite escrita por grupo ou outros")
    with tempfile.TemporaryDirectory(prefix=".forge-archive-", dir=root) as staging:
        package = Path(staging) / ("package.zip" if item["format"] == "zip" else "package.tar.gz")
        binary = Path(staging) / "binary"
        digest = hashlib.sha256()
        total = 0
        check_url(item["url"], initial=True)
        request = Request(item["url"], headers={"User-Agent": "RP-AI-Forge-Archives/2", "Accept": "application/octet-stream"})
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
        copy_selected(package, binary, item["member"], item["platform"], item["format"])
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
        except (OSError, ValueError, RuntimeError, tarfile.TarError, zipfile.BadZipFile, EOFError) as error:
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
