# SPDX-License-Identifier: MIT
"""Forge: resolver explicito de binarios aprovados, nao uma busca irrestrita.
Sem rede por padrao, sem shell, extracao, compilacao ou PATH global.
"""
import argparse
from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import shutil
import stat
import subprocess
import sys
import tempfile
from urllib.parse import urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener

MAX_BYTES = 64 * 1024 * 1024
HOSTS = {"github.com", "release-assets.githubusercontent.com", "objects.githubusercontent.com", "github-releases.githubusercontent.com"}
NAME = re.compile(r"[a-z][a-z0-9_-]{0,63}\Z")


def check_url(url, initial=False):
    value = urlsplit(url)
    if (value.scheme != "https" or value.hostname not in HOSTS or value.username or value.password or value.port not in (None, 443) or value.fragment):
        raise ValueError("Download bloqueado: HTTPS e dominio aprovado sao obrigatorios")
    if initial and (value.hostname != "github.com" or value.query or not re.fullmatch(r"/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+/releases/download/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", value.path)):
        raise ValueError("Exige asset fixo de release GitHub, sem latest ou URL autenticada")
    return url


class ApprovedRedirect(HTTPRedirectHandler):
    max_redirections = 5

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        check_url(newurl)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


@dataclass(frozen=True)
class Asset:
    url: str
    sha256: str
    version: str

    def validate(self):
        check_url(self.url, initial=True)
        if not re.fullmatch(r"[a-f0-9]{64}", self.sha256):
            raise ValueError("SHA-256 fixo e obrigatorio")
        if self.version in ("latest", "") or ("/" + self.version + "/") not in urlsplit(self.url).path:
            raise ValueError("Versao da release deve ser fixa e corresponder a URL")


def platform_key():
    machine = platform.machine().lower()
    arch = {"amd64": "x86_64", "x86_64": "x86_64", "arm64": "aarch64", "aarch64": "aarch64"}.get(machine, machine)
    system = platform.system().lower()
    if os.environ.get("TERMUX_VERSION") or "com.termux" in os.environ.get("PREFIX", ""):
        system = "termux"
    elif system == "android" or hasattr(sys, "getandroidapilevel") or (system == "linux" and os.environ.get("ANDROID_ROOT")):
        system = "android"
    elif system == "linux":
        libc = platform.libc_ver()[0].lower() or "unknown"
        system = "linux-" + libc
    return system + "-" + arch


def _jq(asset, digest):
    return Asset("https://github.com/jqlang/jq/releases/download/jq-1.8.2/" + asset, digest, "jq-1.8.2")


# Digests consultados na API da release oficial; mudancas exigem revisao do codigo.
CATALOG = {"jq": {
    "linux-glibc-x86_64": _jq("jq-linux-amd64", "b1c22172dd303f3be49e935aa56aa48a8b7a46e0bc838b4997d3bb451495870f"),
    "linux-glibc-aarch64": _jq("jq-linux-arm64", "8b85c817833814ddca00a144c33705546355afccf0cf39b188f3cdb48b852309"),
    "darwin-x86_64": _jq("jq-macos-amd64", "e94b266e3c26690550006abe63152b782280f4e14374accdf04cbde844f00bc0"),
    "darwin-aarch64": _jq("jq-macos-arm64", "2d75340ba57a4b4b4c8708a21c2dc8e958a48aaa8bba13b27f77f6e4c0eca07e"),
    "windows-x86_64": _jq("jq-windows-amd64.exe", "a6fc67fedaf9128a3309a1e2ebb8b986aeccf70122ee46d2cb4849e423f0c627"),
    "windows-aarch64": _jq("jq-windows-arm64.exe", "083b5377392bc57cf27052b6d20a2d927770683bca844632901ff38b4b7b0ac7"),
}}


def check_path(path):
    for part in [*reversed(path.parents), path]:
        try:
            info = part.lstat()
        except FileNotFoundError:
            continue
        if stat.S_ISLNK(info.st_mode) or (getattr(info, "st_file_attributes", 0) & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)):
            raise ValueError("Symlink/junction no destino Forge")


def digest_file(path):
    check_path(path)
    if not path.is_file():
        raise ValueError("Destino existente nao e arquivo regular")
    total = 0
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while True:
            block = stream.read(65536)
            if not block:
                break
            total += len(block)
            if total > MAX_BYTES:
                raise ValueError("Binario excede limite")
            digest.update(block)
    return digest.hexdigest()


class Forge:
    def __init__(self, directory=None, catalog=None):
        self.directory = Path(os.path.abspath(os.path.expanduser(str(directory or Path.home() / ".rpa" / "bin"))))
        self.catalog = CATALOG if catalog is None else catalog

    def ensure(self, tool, install=False):
        if not isinstance(tool, str) or not NAME.fullmatch(tool) or tool not in self.catalog:
            raise ValueError("Ferramenta fora do catalogo aprovado")
        check_path(self.directory)
        filename = tool + (".exe" if os.name == "nt" else "")
        target = self.directory / filename
        found = shutil.which(tool)
        if found and Path(os.path.abspath(found)) != target:
            return {"status": "system_available", "path": found, "downloaded": False}
        key = platform_key()
        asset = self.catalog[tool].get(key)
        if asset is None:
            raise ValueError("Sem asset aprovado para " + key + "; nao usa binario de outra ABI")
        asset.validate()
        if target.exists():
            if digest_file(target) != asset.sha256:
                raise ValueError("Binario privado divergente; nao sobrescrito")
            if os.name != "nt" and not os.access(target, os.X_OK):
                raise PermissionError("Binario verificado sem permissao de execucao")
            return {"status": "verified", "path": str(target), "downloaded": False}
        plan = {"status": "download_required", "path": str(target), "platform": key, "version": asset.version, "sha256": asset.sha256, "url": asset.url, "downloaded": False}
        if not install:
            return plan
        self.directory.mkdir(mode=0o700, parents=True, exist_ok=True)
        check_path(self.directory)
        if os.name != "nt" and self.directory.stat().st_mode & 0o022:
            raise PermissionError("Pasta Forge permite escrita de grupo/outros; corrija permissoes antes")
        fd, temporary = tempfile.mkstemp(prefix=".forge-", dir=self.directory)
        try:
            digest = hashlib.sha256()
            total = 0
            header = b""
            opener = build_opener(ApprovedRedirect())
            request = Request(asset.url, headers={"User-Agent": "RP-AI-Forge/0.2", "Accept": "application/octet-stream"})
            with os.fdopen(fd, "wb") as output, opener.open(request, timeout=30) as response:
                check_url(response.geturl())
                while True:
                    block = response.read(65536)
                    if not block:
                        break
                    total += len(block)
                    if total > MAX_BYTES:
                        raise ValueError("Download excede limite de 64 MiB")
                    if not header:
                        header = block[:4]
                    digest.update(block)
                    output.write(block)
            if digest.hexdigest() != asset.sha256:
                raise ValueError("SHA-256 divergente; download descartado")
            allowed = (b"MZ",) if key.startswith("windows-") else ((b"\xcf\xfa\xed\xfe", b"\xce\xfa\xed\xfe", b"\xca\xfe\xba\xbe", b"\xfe\xed\xfa\xcf") if key.startswith("darwin-") else (b"\x7fELF",))
            if not header.startswith(allowed):
                raise ValueError("Nao e binario bruto suportado; scripts e arquivos compactados nao sao executados")
            os.chmod(temporary, 0o700)
            check_path(target)
            # Publicacao exclusiva: nunca substitui arquivo instalado por outro processo.
            os.link(temporary, target)
        finally:
            try:
                os.unlink(temporary)
            except FileNotFoundError:
                pass
        return {**plan, "status": "installed", "downloaded": True}

    def run(self, arguments, repair=False, timeout=120):
        if not arguments or isinstance(arguments, (str, bytes)):
            raise ValueError("Informe lista de argumentos, nao comando de shell")
        result = self.ensure(arguments[0], install=repair)
        if result["status"] == "download_required":
            raise FileNotFoundError("Ferramenta ausente; reparo de rede nao autorizado")
        environment = os.environ.copy()
        environment["PATH"] = str(self.directory) + os.pathsep + environment.get("PATH", "")
        # Uma execucao, sem retry apos erro e sem registrar argumentos ou saida.
        return subprocess.run([result["path"], *arguments[1:]], env=environment, timeout=timeout, shell=False, check=False)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Forge: plano offline ou download aprovado explicito")
    parser.add_argument("action", choices=["plan", "install"])
    parser.add_argument("tool")
    parser.add_argument("--directory", help="Pasta privada, padrao ~/.rpa/bin")
    parser.add_argument("--allow-network", action="store_true")
    args = parser.parse_args(argv)
    if args.action == "install" and not args.allow_network:
        parser.error("install exige --allow-network; use plan para inspecionar sem rede")
    try:
        print(json.dumps(Forge(args.directory).ensure(args.tool, install=args.action == "install"), indent=2))
        return 0
    except (OSError, ValueError, RuntimeError) as error:
        # URL assinada de redirect ou erro bruto HTTP nao vao para logs.
        print("Forge falhou: " + type(error).__name__ + ". Nenhum fallback adicional foi executado.", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
