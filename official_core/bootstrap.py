"""Boot local. Licenca MIT, Copyright 2026 Fabio. Consulte LICENSE.
Uso livre sob MIT, sem garantias adicionais nos limites da lei.
Exibir avisos nao equivale a aceite juridico automatico.
Nao instala pacotes globais, nao eleva privilegios e nao baixa modelos.
"""
import argparse
import json
import os
from pathlib import Path
import sqlite3
import subprocess
import sys
import time
import venv
from .engine import MasterEngine
from .cli import main as run_command

NOTICE = "R.P AI | MIT | Copyright 2026 Fabio. Uso pessoal e comercial permitido, preservando aviso e licenca. Sem garantias adicionais nos limites da lei. Consulte LICENSE e TERMS.md. Termos exibidos, nao aceitos automaticamente. Venv nao e sandbox. Nenhum modelo e baixado."


def detect_system(system=None, environ=None):
    # platform.system() may launch cmd.exe on Windows/Python 3.10.
    # Read the interpreter platform directly; detection must not spawn anything.
    native = {"win32": "windows", "darwin": "darwin", "linux": "linux", "android": "android"}
    name = (native.get(sys.platform, sys.platform) if system is None else system).lower()
    environment = os.environ if environ is None else environ
    if environment.get("TERMUX_VERSION") or "com.termux" in environment.get("PREFIX", ""):
        return "termux"
    if name == "android" or (name == "linux" and (hasattr(sys, "getandroidapilevel") or environment.get("ANDROID_ROOT"))):
        return "android"
    return {"linux": "linux", "windows": "windows", "darwin": "macos"}.get(name, "unsupported")


def install(root=None, create_venv=True):
    if sys.version_info < (3, 10):
        raise RuntimeError("Requer Python 3.10 ou superior")
    system = detect_system()
    if system == "unsupported":
        raise RuntimeError("Sistema ainda nao suportado")
    engine = MasterEngine(root)
    structure = engine.setup_structure()
    connection = engine._database()
    connection.close()
    result = {"status": "core_ready", "system": system, "workspace": structure["workspace"], "models_downloaded": False, "network_started": False, "system_packages_installed": False, "venv": None}
    if create_venv:
        directory = engine.path("AI_Local_Engine/ai_env")
        interpreter = engine.path("AI_Local_Engine/ai_env/" + ("Scripts/python.exe" if os.name == "nt" else "bin/python"))
        if directory.exists() and not interpreter.is_file():
            raise RuntimeError("Venv incompleto existente; preserve dados e use --no-venv ou outro workspace")
        if not directory.exists():
            # Biblioteca padrao: sem ensurepip, sem atualizacao e sem rede.
            venv.EnvBuilder(with_pip=False, symlinks=False, clear=False, upgrade_deps=False).create(str(directory))
        engine._check_chain(interpreter)
        if not interpreter.is_file():
            raise RuntimeError("Criacao de venv nao foi confirmada")
        probe = subprocess.run([str(interpreter), "-I", "-c", "import json,sys; print(json.dumps(dict(prefix=sys.prefix,version=list(sys.version_info[:2]))))"], check=True, capture_output=True, text=True, timeout=20, shell=False)
        info = json.loads(probe.stdout)
        if Path(info["prefix"]).resolve() != directory.resolve() or tuple(info["version"]) < (3, 10):
            raise RuntimeError("Interpretador do ambiente nao corresponde ao workspace")
        result["venv"] = str(interpreter)
    return result


def bootstrap(root=".core", create_venv=True):
    result = install(root, create_venv)
    engine = MasterEngine(root)
    ai = engine.deploy_ai_engine(create_venv=False)
    if create_venv:
        ai = {"status": "venv_ready", "python": result["venv"]}
    result.update({"status": "boot_complete", "ai_environment": ai, "global_packages_installed": False, "inference_implemented": False, "diagnostics": engine.doctor()})
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description="Boot offline R.P AI, sem interacao ou sudo")
    parser.add_argument("--root", default=".core", help="Workspace dedicado")
    parser.add_argument("--without-venv", "--no-venv", action="store_true", help="Prepara ferramentas sem criar venv")
    parser.add_argument("--run", nargs=argparse.REMAINDER, help="Comando local depois do boot; exemplo: --run note-list")
    args = parser.parse_args(argv)
    if args.run is not None and not args.run:
        parser.error("Informe um comando depois de --run")
    if args.run and any(token == "--root" or token.startswith("--root=") for token in args.run):
        parser.error("Configure --root antes de --run")
    print(NOTICE, file=sys.stderr)
    started = time.monotonic()
    # Tardio: launcher importa install deste modulo.
    from .launcher import write_report
    try:
        result = bootstrap(args.root, create_venv=not args.without_venv)
        result["report"] = write_report(args.root, "boot", True, started)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return run_command(["--root", args.root] + args.run) if args.run else 0
    except (OSError, ValueError, RuntimeError, sqlite3.Error, subprocess.SubprocessError) as error:
        message = "Verificacao do interpretador falhou" if isinstance(error, subprocess.SubprocessError) else str(error)
        print("Boot falhou: " + message, file=sys.stderr)
        print("Nenhuma instalacao global foi tentada. Veja docs/TERMINALS.md e preserve o workspace.", file=sys.stderr)
        try:
            write_report(args.root, "boot", False, started, type(error).__name__)
        except (OSError, ValueError, RuntimeError, sqlite3.Error):
            print("Relatorio indisponivel", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
