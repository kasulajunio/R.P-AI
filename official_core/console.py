# SPDX-License-Identifier: MIT
"""Entrada de produto: comandos reais, status somente leitura e versao coerente."""
import json
import os
import platform
from pathlib import Path
import sqlite3
import subprocess
import sys
import time
from . import launcher
from .bootstrap import detect_system
from .engine import MasterEngine

VERSION = "0.2.0"


def status(root, source):
    engine = MasterEngine(root)
    database = engine.path("Database_Nexus/notes.sqlite3")
    health = {"state": "not_initialized", "ok": None, "encrypted": False}
    if database.exists():
        if not database.is_file():
            raise ValueError("Banco existente nao e arquivo regular")
        connection = None
        try:
            # URI somente leitura; nao cria banco, tabelas nem dados de exemplo.
            connection = sqlite3.connect(database.as_uri() + "?mode=ro", uri=True, timeout=5)
            connection.execute("PRAGMA query_only=ON")
            checks = [row[0] for row in connection.execute("PRAGMA quick_check")]
            health = {"state": "checked", "ok": checks == ["ok"], "encrypted": False}
        except sqlite3.Error as error:
            health = {"state": "unreadable", "ok": False, "error_type": type(error).__name__, "encrypted": False}
        finally:
            if connection is not None:
                connection.close()
    directory = engine.path("AI_Local_Engine/ai_env")
    interpreter = directory / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    engine._check_chain(interpreter)
    reports = []
    logs = engine.path("logs")
    if logs.is_dir():
        for report in logs.glob("*.json"):
            engine._check_chain(report)
            if report.is_file():
                reports.append(report)
    latest = max(reports, key=lambda path: path.stat().st_mtime_ns) if reports else None
    commit = None
    repository = Path(source).resolve()
    if (repository / ".git").exists():
        try:
            if Path(launcher._git(repository, "rev-parse", "--show-toplevel")).resolve() == repository:
                commit = launcher._git(repository, "rev-parse", "--short", "HEAD")
        except (OSError, subprocess.SubprocessError):
            pass
    return {"version": VERSION, "system": detect_system(), "python": platform.python_version(), "workspace": str(engine.base_dir), "configured": engine.path("core.json").is_file(), "database": health, "venv_python_exists": interpreter.is_file(), "venv_integrity": "not_checked_by_status", "commit": commit, "latest_previous_report": str(latest) if latest else None, "available_commands": ["notes", "tasks", "export", "backup", "sha256", "doctor"], "inference_implemented": False, "model_installed_by_rpa": False, "background_service_started": False, "warning": "Venv nao e sandbox. Presenca de arquivo nao comprova integridade. Nenhum modelo foi executado"}


def build_parser():
    parser = launcher.build_parser()
    parser.description = "R.P AI: install, run, update, status e autoload explicitos"
    parser.add_argument("--version", action="version", version="R.P AI " + VERSION)
    for action in parser._actions:
        if hasattr(action, "add_parser"):
            action.add_parser("status", help="Diagnostico local sem rede ou execucao de modelo")
            break
    return parser


def main(argv=None):
    arguments = list(sys.argv[1:] if argv is None else argv)
    args = build_parser().parse_args(arguments)
    if args.command == "run":
        # Um comando nao deve escapar do workspace configurado nem separar os logs.
        nested = args.arguments or []
        if "--root" in nested or any(value.startswith("--root=") for value in nested):
            print("Defina --root antes de run, nao dentro do comando", file=sys.stderr)
            return 1
    if args.command != "status":
        return launcher.main(arguments)
    started = time.monotonic()
    try:
        result = status(args.root, args.source)
        healthy = result["database"]["ok"] is not False
        result["report"] = launcher.write_report(args.root, "status", healthy, started)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if healthy else 1
    except (OSError, ValueError, RuntimeError, sqlite3.Error) as error:
        print("Falha no status: " + type(error).__name__, file=sys.stderr)
        try:
            launcher.write_report(args.root, "status", False, started, type(error).__name__)
        except (OSError, ValueError, RuntimeError):
            print("Relatorio indisponivel", file=sys.stderr)
        return 1
