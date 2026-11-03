# SPDX-License-Identifier: MIT
"""Boot nao interativo: prepara ferramentas locais, sem instalar pacotes globais."""
import argparse
import json
import os
import platform
import subprocess
import sys
from .engine import MasterEngine
from .cli import main as run_command

TERMS = """R.P AI - Copyright 2026 Fabio - Licenca MIT.
Uso, copia, modificacao, distribuicao e uso comercial permitidos,
preservando o aviso de copyright e a licenca. Consulte LICENSE e TERMS.md.
Software fornecido no estado em que se encontra, sem garantias adicionais,
nos limites permitidos pela lei. O operador responde pelo proprio uso.
Isto e um aviso, nao uma declaracao de aceite automatico.
Venv nao e sandbox. Nenhum modelo e baixado ou executado neste boot.
"""


def detect_system(system=None, environ=None):
    environment = os.environ if environ is None else environ
    name = (platform.system() if system is None else system).lower()
    if environment.get("TERMUX_VERSION") or "com.termux" in environment.get("PREFIX", ""):
        return "termux"
    if name == "android" or (name == "linux" and environment.get("ANDROID_ROOT")):
        return "android"
    known = {"linux": "linux", "windows": "windows", "darwin": "macos"}
    if name not in known:
        raise RuntimeError("Sistema nao suportado: " + name)
    return known[name]


def bootstrap(root=".core", create_venv=True):
    if sys.version_info < (3, 10):
        raise RuntimeError("Python 3.10 ou superior e obrigatorio")
    system = detect_system()
    engine = MasterEngine(root)
    structure = engine.setup_structure()
    database = engine._database()
    database.close()
    ai = engine.deploy_ai_engine(create_venv=create_venv)
    if create_venv:
        # Executa o Python do ambiente criado, sem shell e sem ativacao manual.
        subprocess.run([ai["python"], "-I", "-c", "import sys; assert sys.prefix != sys.base_prefix; print(sys.version.split()[0])"], check=True, capture_output=True, text=True, timeout=30, shell=False)
    return {"system": system, "status": "boot_complete", "workspace": structure["workspace"], "ai_environment": ai, "global_packages_installed": False, "models_downloaded": False, "inference_implemented": False, "network_started": False, "diagnostics": engine.doctor()}


def main(argv=None):
    parser = argparse.ArgumentParser(description="Boot offline R.P AI, sem interacao ou sudo")
    parser.add_argument("--root", default=".core", help="Workspace dedicado")
    parser.add_argument("--without-venv", action="store_true", help="Prepara ferramentas sem criar venv")
    parser.add_argument("--run", nargs=argparse.REMAINDER, help="Comando local depois do boot; exemplo: --run note-list")
    args = parser.parse_args(argv)
    if args.run is not None and not args.run:
        parser.error("Informe um comando depois de --run")
    if args.run and (args.run[0] == "--root" or "--root" in args.run):
        parser.error("Configure o workspace com --root antes de --run")
    print(TERMS)
    try:
        result = bootstrap(args.root, create_venv=not args.without_venv)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        if args.run:
            return run_command(["--root", args.root] + args.run)
        return 0
    except (OSError, ValueError, RuntimeError, subprocess.SubprocessError) as error:
        print("Boot falhou: " + str(error), file=sys.stderr)
        print("Nenhuma instalacao global foi tentada. Veja docs/TERMINALS.md e preserve o workspace existente.", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
