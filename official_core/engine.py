"""Motor local: nenhum download, modelo ou tunel e iniciado implicitamente."""
from __future__ import annotations

import hashlib
import json
import os
import platform
import re
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import threading
import weakref
import venv
from pathlib import Path

MODULES = {
    "1": "AI_Local_Engine",
    "2": "Crypto_Vault",
    "3": "Database_Nexus",
    "4": "Gaming_Environment",
    "5": "Network_Tunnels",
}
ALIASES = {"ai": "1", "crypto": "2", "db": "3", "gaming": "4", "network": "5"}
RESERVED = {"CON", "PRN", "AUX", "NUL"} | {f"COM{x}" for x in range(1, 10)} | {f"LPT{x}" for x in range(1, 10)}


class SafetyError(ValueError):
    """Uma operacao de sistema de arquivos foi recusada."""


_DATABASE_LOCKS = weakref.WeakValueDictionary()
_DATABASE_LOCKS_GUARD = threading.Lock()


class _SerializedConnection(sqlite3.Connection):
    """Keep the per-file local queue until the operation closes."""
    def close(self):
        lock = getattr(self, "_operation_lock", None)
        try:
            super().close()
        finally:
            if lock is not None:
                self._operation_lock = None
                lock.release()


class MasterEngine:
    def __init__(self, base_dir=None):
        root = Path(base_dir) if base_dir is not None else Path.cwd() / "Fabio_Official_Core"
        if ".." in root.parts:
            raise SafetyError("A raiz nao pode conter ..")
        root = root.expanduser().absolute()
        if root == Path(root.anchor):
            raise SafetyError("Nao use a raiz do sistema como workspace")
        self.base_dir = root
        self.modules = dict(MODULES)
        self._check_chain(root)

    @staticmethod
    def _check_chain(path):
        for item in (path, *path.parents):
            junction = getattr(item, "is_junction", None)
            if item.is_symlink() or (junction is not None and junction()):
                raise SafetyError("Links simbolicos e junctions nao sao aceitos")

    def path(self, relative):
        value = str(relative)
        if not value or value.startswith("/") or "\\" in value or "\x00" in value:
            raise SafetyError("Caminho relativo invalido")
        parts = value.split("/")
        for part in parts:
            if part in ("", ".", "..") or not re.fullmatch(r"[A-Za-z0-9_.-]+", part):
                raise SafetyError("Nome de arquivo nao portavel")
            if part.endswith((".", " ")) or part.split(".")[0].upper() in RESERVED:
                raise SafetyError("Nome reservado pelo sistema")
        candidate = self.base_dir.joinpath(*parts)
        self._check_chain(candidate)
        candidate.relative_to(self.base_dir)
        return candidate

    def _mkdir(self, relative):
        target = self.path(relative)
        target.mkdir(parents=True, exist_ok=True, mode=0o700)
        self._check_chain(target)
        return target

    def _write_new(self, relative, content):
        target = self.path(relative)
        target.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        self._check_chain(target)
        if target.exists():
            if not target.is_file():
                raise SafetyError("O destino existente nao e arquivo regular")
            return False
        descriptor, temporary = tempfile.mkstemp(prefix=".rpa-write-", dir=target.parent)
        staging = Path(temporary)
        try:
            with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
                stream.write(content)
                stream.flush()
                os.fsync(stream.fileno())
            self._check_chain(target)
            try:
                # Publish the completed file exclusively; never expose partial writes.
                os.link(staging, target)
            except FileExistsError:
                if not target.is_file():
                    raise SafetyError("O destino existente nao e arquivo regular")
                return False
            return True
        finally:
            staging.unlink(missing_ok=True)

    def setup_structure(self):
        self._check_chain(self.base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
        for name in MODULES.values():
            self._mkdir(name)
        config = {"schema": 1, "owner": "Fabio", "network_enabled": False, "automatic_downloads": False, "modules": MODULES}
        self._write_new("core.json", json.dumps(config, ensure_ascii=False, indent=2) + "\n")
        self._write_new("Crypto_Vault/AVISO.txt", "NAO E COFRE CRIPTOGRAFADO. Nao armazene senhas, chaves privadas ou seeds. SHA-256 so verifica integridade.\n")
        return {"workspace": str(self.base_dir), "modules": list(MODULES.values()), "status": "structure_ready"}

    def check_nvidia_gpu(self):
        binary = shutil.which("nvidia-smi")
        if not binary:
            return False
        try:
            result = subprocess.run([binary, "--query-gpu=name", "--format=csv,noheader"], shell=False, capture_output=True, text=True, timeout=5, check=False)
            return result.returncode == 0 and bool(result.stdout.strip())
        except (OSError, subprocess.SubprocessError):
            return False

    def doctor(self):
        android = hasattr(sys, "getandroidapilevel") or "com.termux" in os.environ.get("PREFIX", "")
        return {
            "python": platform.python_version(),
            "system": platform.system(),
            "architecture": platform.machine(),
            "android_or_termux": android,
            "venv_available": bool(getattr(venv, "EnvBuilder", None)),
            "nvidia_smi_available": self.check_nvidia_gpu(),
            "cuda_compatibility": "not_validated",
            "network_started": False,
            "warning": "Venv nao e sandbox de seguranca. Ausencia de nvidia-smi nao prova ausencia de GPU.",
        }

    def deploy_ai_engine(self, create_venv=False):
        self.setup_structure()
        ai_dir = self._mkdir(MODULES["1"])
        self._write_new("AI_Local_Engine/README.txt", "Ambiente preparado, sem modelo ou bibliotecas ML instalados. Consulte docs/AI_LOCAL.md no repositorio.\n")
        env_dir = self.path("AI_Local_Engine/ai_env")
        python_path = env_dir / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
        if create_venv:
            if env_dir.exists() and not python_path.is_file():
                raise SafetyError("Ambiente incompleto existente; preserve os dados e escolha outro workspace")
            if not env_dir.exists():
                venv.EnvBuilder(with_pip=True, clear=False, upgrade_deps=False).create(str(env_dir))
            if not python_path.is_file():
                raise RuntimeError("Criacao do ambiente virtual nao foi confirmada")
        self._write_new("AI_Local_Engine/run_ai_test.py", "import importlib.util\nimport sys\nprint(sys.version)\nif importlib.util.find_spec(\"torch\") is None:\n    print(\"PyTorch nao instalado. Nenhum modelo foi baixado.\")\nelse:\n    import torch\n    print(torch.__version__)\n    print(\"CUDA disponivel:\", torch.cuda.is_available())\n")
        return {"module": MODULES["1"], "status": "venv_ready" if create_venv else "prepared", "python": str(python_path) if create_venv else None, "models_downloaded": False, "directory": str(ai_dir)}

    def _database(self):
        self.setup_structure()
        path = self.path("Database_Nexus/notes.sqlite3")
        if path.exists() and not path.is_file():
            raise SafetyError("Banco existente nao e arquivo regular")
        # Cria o arquivo com permissoes restritas em POSIX antes de conectar.
        self._write_new("Database_Nexus/notes.sqlite3", "")
        # Queue same-process operations: SQLite has one writer, and the
        # five-second busy timeout starved competing Windows threads.
        key = os.path.normcase(str(path.absolute()))
        with _DATABASE_LOCKS_GUARD:
            lock = _DATABASE_LOCKS.get(key)
            if lock is None:
                lock = threading.RLock()
                _DATABASE_LOCKS[key] = lock
        if not lock.acquire(timeout=30):
            raise sqlite3.OperationalError("database local queue timed out")
        connection = None
        try:
            connection = sqlite3.connect(str(path), timeout=30, factory=_SerializedConnection)
            connection._operation_lock = lock
            connection.execute("PRAGMA foreign_keys=ON")
            connection.execute("CREATE TABLE IF NOT EXISTS notes (id INTEGER PRIMARY KEY, title TEXT NOT NULL, body TEXT NOT NULL, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)")
            connection.commit()
            return connection
        except BaseException:
            if connection is not None:
                connection.close()
            else:
                lock.release()
            raise

    def add_note(self, title, body=""):
        if not isinstance(title, str) or not title.strip() or len(title) > 200:
            raise ValueError("Titulo deve ter entre 1 e 200 caracteres")
        if not isinstance(body, str) or len(body) > 10000:
            raise ValueError("Texto limitado a 10000 caracteres")
        connection = self._database()
        try:
            with connection:
                cursor = connection.execute("INSERT INTO notes(title,body) VALUES (?,?)", (title.strip(), body))
                return {"id": cursor.lastrowid, "status": "saved_local_unencrypted"}
        finally:
            connection.close()

    def list_notes(self, limit=20):
        if type(limit) is not int or not 1 <= limit <= 100:
            raise ValueError("Limite deve ser inteiro entre 1 e 100")
        connection = self._database()
        try:
            rows = connection.execute("SELECT id,title,body,created_at FROM notes ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
            return [dict(zip(("id", "title", "body", "created_at"), row)) for row in rows]
        finally:
            connection.close()

    def install_module(self, choice, create_venv=False):
        choice = ALIASES.get(str(choice), str(choice))
        if choice not in MODULES:
            raise ValueError("Modulo invalido; escolha 1 a 5 ou ai, crypto, db, gaming, network")
        if create_venv and choice != "1":
            raise ValueError("A opcao --venv pertence somente ao modulo ai")
        if choice == "1":
            return self.deploy_ai_engine(create_venv)
        self.setup_structure()
        if choice == "3":
            connection = self._database()
            connection.close()
        if choice == "4":
            self._write_new("Gaming_Environment/session.json", json.dumps({"schema": 1, "project": "local-prototype", "engine": None, "automatic_execution": False}, indent=2) + "\n")
        if choice == "5":
            self._write_new("Network_Tunnels/config.json", json.dumps({"schema": 1, "enabled": False, "bind": "127.0.0.1", "port": None, "tunneling_implemented": False}, indent=2) + "\n")
        return {"module": MODULES[choice], "status": "prepared", "network_started": False}


def sha256_file(filename, max_bytes=1024 * 1024 * 1024):
    path = Path(filename)
    if path.is_symlink() or not path.is_file():
        raise SafetyError("Escolha um arquivo regular, nao um link")
    if path.stat().st_size > max_bytes:
        raise ValueError("Arquivo excede o limite de leitura")
    digest = hashlib.sha256()
    total = 0
    with path.open("rb") as stream:
        while True:
            block = stream.read(1024 * 1024)
            if not block:
                break
            total += len(block)
            if total > max_bytes:
                raise ValueError("Arquivo cresceu alem do limite")
            digest.update(block)
    return {"sha256": digest.hexdigest(), "bytes": total}
