"""CLI rpa: operacoes explicitas, relatorios sem argumentos sensiveis."""
import argparse
import json
import os
from pathlib import Path
import shlex
import sqlite3
import subprocess
import sys
import time
import uuid
from datetime import datetime, timezone
from .bootstrap import NOTICE, install
from .cli import main as core_main
from .engine import MasterEngine

DEFAULT_SOURCE = Path(__file__).resolve().parents[1]
OFFICIAL_REMOTES = {"https://github.com/kasulajunio/R.P-AI.git", "https://github.com/kasulajunio/R.P-AI", "git@github.com:kasulajunio/R.P-AI.git"}


def _git(source, *arguments):
    result = subprocess.run(["git", "-C", str(source), *arguments], check=True, capture_output=True, text=True, timeout=120, shell=False)
    return result.stdout.strip()


def update(source):
    source = Path(source).resolve()
    if not (source / ".git").exists():
        raise ValueError("Atualizacao exige clone Git; ZIP e instalacao em wheel nao usam git pull")
    if Path(_git(source, "rev-parse", "--show-toplevel")).resolve() != source:
        raise ValueError("Selecione a raiz do clone oficial")
    if _git(source, "status", "--porcelain"):
        raise ValueError("Alteracoes locais: salve ou revise antes de atualizar")
    if _git(source, "symbolic-ref", "--short", "HEAD") != "main":
        raise ValueError("Atualizacao automatica exige branch main")
    if _git(source, "remote", "get-url", "origin") not in OFFICIAL_REMOTES:
        raise ValueError("Origin nao corresponde ao repositorio oficial")
    _git(source, "pull", "--ff-only", "origin", "main")
    return {"status": "updated", "commit": _git(source, "rev-parse", "HEAD"), "dependencies_installed": False}


def write_report(root, command, success, started, error_type=None):
    engine = MasterEngine(root)
    record = {"schema": 1, "command": command, "success": success, "duration_ms": round((time.monotonic() - started) * 1000), "utc": datetime.now(timezone.utc).isoformat(), "error_type": error_type}
    relative = "logs/" + uuid.uuid4().hex + ".json"
    if not engine._write_new(relative, json.dumps(record, indent=2) + "\n"):
        raise RuntimeError("Nao foi possivel criar relatorio exclusivo")
    return str(engine.path(relative))


def autoload(root, source, target, auto_update=False):
    source = Path(source).resolve()
    engine = MasterEngine(root)
    engine.setup_structure()
    arguments = [sys.executable, str(source / "autoload.py"), "--root", str(engine.base_dir), "--source", str(source)]
    if auto_update:
        arguments.append("--auto-update")
    if any("\n" in value or "\r" in value for value in arguments):
        raise ValueError("Caminhos com quebras de linha nao sao aceitos")
    if target == "linux":
        relative = "Autoload/rp-ai.service"
        command = shlex.join(arguments).replace("%", "%%")
        content = "[Unit]\nDescription=R.P AI startup (user)\n\n[Service]\nType=oneshot\nExecStart=" + command + "\n\n[Install]\nWantedBy=default.target\n"
    elif target == "termux":
        relative = "Autoload/rp-ai-termux.sh"
        content = "#!/data/data/com.termux/files/usr/bin/sh\nset -eu\nexec " + shlex.join(arguments) + "\n"
    elif target == "windows":
        relative = "Autoload/rp-ai.ps1"
        quote = chr(39)
        content = "& " + " ".join(quote + value.replace(quote, quote * 2) + quote for value in arguments) + "\nexit $LASTEXITCODE\n"
    else:
        raise ValueError("Autoload disponivel para linux, termux ou windows")
    if not engine._write_new(relative, content):
        raise FileExistsError("Template existente; preserve-o e escolha outro workspace")
    return {"status": "template_created", "path": str(engine.path(relative)), "activated": False, "auto_update": auto_update}


def build_parser():
    parser = argparse.ArgumentParser(prog="rpa", description="R.P AI: install, run, update e autoload explicitos")
    parser.add_argument("--root", default=".core", help="Workspace local de dados e logs")
    parser.add_argument("--source", default=str(DEFAULT_SOURCE), help="Raiz do clone oficial para update/autoload")
    commands = parser.add_subparsers(dest="command", required=True)
    setup = commands.add_parser("install")
    setup.add_argument("--no-venv", action="store_true")
    run = commands.add_parser("run")
    run.add_argument("arguments", nargs=argparse.REMAINDER)
    commands.add_parser("update", help="Usa rede; somente main limpo, origin oficial e fast-forward")
    auto = commands.add_parser("autoload", help="Gera template; nao ativa servicos")
    auto.add_argument("--platform", choices=["linux", "termux", "windows"], required=True)
    auto.add_argument("--auto-update", action="store_true", help="Autoriza pull via rede a cada execucao do template")
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    started = time.monotonic()
    try:
        if args.command == "install":
            print(NOTICE, file=sys.stderr)
            result = install(args.root, not args.no_venv)
        elif args.command == "update":
            result = update(args.source)
        elif args.command == "autoload":
            result = autoload(args.root, args.source, args.platform, args.auto_update)
        else:
            code = core_main(["--root", args.root] + (args.arguments or ["doctor"]))
            log = write_report(args.root, "run", code == 0, started)
            print("Relatorio: " + log, file=sys.stderr)
            return code
        result["report"] = write_report(args.root, args.command, True, started)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (OSError, ValueError, RuntimeError, sqlite3.Error, subprocess.SubprocessError) as error:
        # Sem stderr de subprocessos: URLs de autenticacao podem conter dados privados.
        print("Falha " + type(error).__name__ + ": " + ("Comando externo falhou; verifique instalacao/permissoes/rede" if isinstance(error, subprocess.SubprocessError) else str(error)), file=sys.stderr)
        try:
            log = write_report(args.root, args.command, False, started, type(error).__name__)
            print("Relatorio: " + log, file=sys.stderr)
        except (OSError, ValueError, RuntimeError) as log_error:
            print("Relatorio indisponivel: " + type(log_error).__name__, file=sys.stderr)
        return 1
