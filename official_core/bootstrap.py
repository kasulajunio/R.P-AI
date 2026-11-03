"""Boot local. Licenca MIT, Copyright 2026 Fabio. Consulte LICENSE.
Uso, copia, modificacao e distribuicao permitidos sob MIT. Sem garantia, nos
limites da lei. Aviso exibido nao equivale a aceite juridico automatico.
Nao instala pacotes do sistema, nao eleva privilegios e nao baixa modelos.
"""
import json
import os
import platform
import subprocess
import sys
import venv
from .engine import MasterEngine

NOTICE = "R.P AI | MIT | Copyright 2026 Fabio. Sem garantia, nos limites da lei. Consulte LICENSE e TERMS.md. Termos exibidos, nao aceitos automaticamente."


def detect_system(system=None, environ=None):
    system = platform.system() if system is None else system
    environ = os.environ if environ is None else environ
    if environ.get("TERMUX_VERSION") or "com.termux" in environ.get("PREFIX", ""):
        return "termux"
    if system.lower() == "android" or (system == "Linux" and hasattr(sys, "getandroidapilevel")):
        return "android"
    return {"Linux": "linux", "Windows": "windows", "Darwin": "macos"}.get(system, "unsupported")


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
            # Sem ensurepip nem rede: nucleo usa exclusivamente a biblioteca padrao.
            venv.EnvBuilder(with_pip=False, symlinks=False, clear=False, upgrade_deps=False).create(str(directory))
        engine._check_chain(interpreter)
        if not interpreter.is_file():
            raise RuntimeError("Criacao de venv nao foi confirmada")
        probe = subprocess.run([str(interpreter), "-I", "-c", "import json,sys; print(json.dumps(dict(prefix=sys.prefix,version=list(sys.version_info[:2]))))"], check=True, capture_output=True, text=True, timeout=20, shell=False)
        info = json.loads(probe.stdout)
        from pathlib import Path
        if Path(info["prefix"]).resolve() != directory.resolve() or tuple(info["version"]) < (3, 10):
            raise RuntimeError("Interpretador do ambiente nao corresponde ao workspace")
        result["venv"] = str(interpreter)
    return result
