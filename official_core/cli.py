"""R.P AI: comandos locais, com operacoes destrutivas explicitas."""
import argparse
import json
import sqlite3
import sys
from .engine import MasterEngine, sha256_file
from .services import Notes, Tasks, Database


def output(value):
    print(json.dumps(value, ensure_ascii=False, indent=2))


def build_parser():
    parser = argparse.ArgumentParser(description="R.P AI: ferramentas locais de Fabio")
    parser.add_argument("--root", help="Workspace dedicado; padrao ./Fabio_Official_Core")
    commands = parser.add_subparsers(dest="command")
    for name in ("init", "doctor", "modules", "db-check"):
        commands.add_parser(name)
    prepare = commands.add_parser("prepare")
    prepare.add_argument("module", choices=["1", "2", "3", "4", "5", "ai", "crypto", "db", "gaming", "network"])
    prepare.add_argument("--venv", action="store_true", help="Cria venv para IA, sem bibliotecas ML ou modelos")
    hashing = commands.add_parser("sha256", help="Integridade, nao criptografia")
    hashing.add_argument("file")
    add = commands.add_parser("note-add")
    add.add_argument("title")
    add.add_argument("--body", default="")
    listing = commands.add_parser("note-list")
    listing.add_argument("--limit", type=int, default=20)
    get = commands.add_parser("note-get")
    get.add_argument("id", type=int)
    search = commands.add_parser("note-search")
    search.add_argument("query")
    search.add_argument("--limit", type=int, default=20)
    update = commands.add_parser("note-update")
    update.add_argument("id", type=int)
    update.add_argument("--title")
    update.add_argument("--body")
    delete = commands.add_parser("note-delete", help="Exclui uma nota, nao todo o banco")
    delete.add_argument("id", type=int)
    delete.add_argument("--confirm", action="store_true")
    export = commands.add_parser("note-export")
    export.add_argument("name", help="Nome .json; nao sobrescreve arquivos")
    task_add = commands.add_parser("task-add", help="Tarefa local, sem notificacao automatica")
    task_add.add_argument("title")
    task_list = commands.add_parser("task-list")
    task_list.add_argument("--state", choices=["open", "done", "all"], default="open")
    task_list.add_argument("--limit", type=int, default=20)
    task_done = commands.add_parser("task-done")
    task_done.add_argument("id", type=int)
    task_done.add_argument("--reopen", action="store_true")
    backup = commands.add_parser("db-backup")
    backup.add_argument("name", help="Nome .sqlite3; nao sobrescreve backups")
    return parser


def dispatch(engine, args):
    command = args.command
    if command == "init":
        return engine.setup_structure()
    if command == "doctor":
        return engine.doctor()
    if command == "modules":
        return engine.modules
    if command == "prepare":
        return engine.install_module(args.module, args.venv)
    if command == "sha256":
        return sha256_file(args.file)
    if command == "note-add":
        return engine.add_note(args.title, args.body)
    if command == "note-list":
        return engine.list_notes(args.limit)
    if command == "note-get":
        return Notes(engine).get(args.id)
    if command == "note-search":
        return Notes(engine).search(args.query, args.limit)
    if command == "note-update":
        return Notes(engine).update(args.id, args.title, args.body)
    if command == "note-delete":
        return Notes(engine).delete(args.id, args.confirm)
    if command == "note-export":
        return Notes(engine).export(args.name)
    if command == "task-add":
        return Tasks(engine).add(args.title)
    if command == "task-list":
        return Tasks(engine).list(args.state, args.limit)
    if command == "task-done":
        return Tasks(engine).set_done(args.id, not args.reopen)
    if command == "db-check":
        return Database(engine).check()
    if command == "db-backup":
        return Database(engine).backup(args.name)
    raise ValueError("Comando desconhecido")


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command is None:
        parser.print_help()
        return 0
    try:
        output(dispatch(MasterEngine(args.root), args))
        return 0
    except (OSError, ValueError, RuntimeError, sqlite3.Error) as error:
        print("Erro: " + str(error), file=sys.stderr)
        return 1


def menu():
    engine = MasterEngine()
    print("R.P AI | ferramentas locais de Fabio | sem downloads automaticos")
    print("Crypto_Vault nao e cofre criptografado. Venv nao e sandbox.")
    print("Use --help para notas, tarefas, exportacao e backups.")
    while True:
        for key, value in engine.modules.items():
            print(key + ". " + value)
        print("0. Sair")
        try:
            choice = input("Escolha: ").strip()
            if choice == "0":
                return 0
            output(engine.install_module(choice))
        except (EOFError, KeyboardInterrupt):
            print("\nEncerrado.")
            return 0
        except (OSError, ValueError, RuntimeError, sqlite3.Error) as error:
            print("Erro: " + str(error), file=sys.stderr)
