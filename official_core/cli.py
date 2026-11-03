"""Interface sem instalacoes ou conexoes implicitas."""
import argparse
import json
import sqlite3
import sys
from .engine import MasterEngine, sha256_file


def output(value):
    print(json.dumps(value, ensure_ascii=False, indent=2))


def main(argv=None):
    parser = argparse.ArgumentParser(description="Fabio Official Core: fundacao modular privada")
    parser.add_argument("--root", help="Workspace dedicado; padrao ./Fabio_Official_Core")
    commands = parser.add_subparsers(dest="command")
    commands.add_parser("init", help="Cria estrutura sem downloads")
    commands.add_parser("doctor", help="Diagnostico local; nao instala componentes")
    commands.add_parser("modules", help="Lista os cinco modulos")
    prepare = commands.add_parser("prepare", help="Prepara um modulo")
    prepare.add_argument("module", choices=["1", "2", "3", "4", "5", "ai", "crypto", "db", "gaming", "network"])
    prepare.add_argument("--venv", action="store_true", help="Cria ambiente virtual para IA, sem baixar bibliotecas ou modelos")
    hashing = commands.add_parser("sha256", help="Calcula integridade, nao cifra arquivos")
    hashing.add_argument("file")
    add = commands.add_parser("note-add", help="Nota SQLite local SEM criptografia")
    add.add_argument("title")
    add.add_argument("--body", default="")
    listing = commands.add_parser("note-list")
    listing.add_argument("--limit", type=int, default=20)
    args = parser.parse_args(argv)
    if args.command is None:
        parser.print_help()
        return 0
    try:
        engine = MasterEngine(args.root)
        if args.command == "init":
            result = engine.setup_structure()
        elif args.command == "doctor":
            result = engine.doctor()
        elif args.command == "modules":
            result = engine.modules
        elif args.command == "prepare":
            result = engine.install_module(args.module, args.venv)
        elif args.command == "sha256":
            result = sha256_file(args.file)
        elif args.command == "note-add":
            result = engine.add_note(args.title, args.body)
        else:
            result = engine.list_notes(args.limit)
        output(result)
        return 0
    except (OSError, ValueError, RuntimeError, sqlite3.Error) as error:
        print("Erro: " + str(error), file=sys.stderr)
        return 1


def menu():
    engine = MasterEngine()
    print("Fabio Official Core | repositorio privado | sem downloads automaticos")
    print("Crypto_Vault nao e cofre criptografado. Venv nao e sandbox.")
    while True:
        for key, value in engine.modules.items():
            print(key + ". " + value)
        print("0. Sair")
        try:
            choice = input("Escolha: ").strip()
            if choice == "0":
                return 0
            # O menu cria somente a base. --venv exige comando explicito.
            output(engine.install_module(choice))
        except (EOFError, KeyboardInterrupt):
            print("\nEncerrado.")
            return 0
        except (OSError, ValueError, RuntimeError, sqlite3.Error) as error:
            print("Erro: " + str(error), file=sys.stderr)
