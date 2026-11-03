"""Servicos locais reais. Sem rede, shell, telemetria ou criptografia implicita."""
import json
import re
import sqlite3
from contextlib import contextmanager


def positive_id(value):
    if type(value) is not int or not 1 <= value <= 2**63 - 1:
        raise ValueError("ID deve ser inteiro positivo de 64 bits")
    return value


def text(value, maximum, label, required=True):
    if not isinstance(value, str) or len(value) > maximum or (required and not value.strip()):
        raise ValueError(label + " invalido ou muito longo")
    return value.strip() if required else value


def bounded_limit(value):
    if type(value) is not int or not 1 <= value <= 100:
        raise ValueError("Limite deve estar entre 1 e 100")
    return value


def filename(value, suffix):
    if not isinstance(value, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,79}", value) or not value.endswith(suffix):
        raise ValueError("Nome simples obrigatorio, com extensao " + suffix)
    return value


class LocalStore:
    def __init__(self, engine):
        self.engine = engine

    @contextmanager
    def connection(self):
        connection = self.engine._database()
        connection.row_factory = sqlite3.Row
        try:
            with connection:
                yield connection
        finally:
            connection.close()


class Notes(LocalStore):
    def get(self, note_id):
        positive_id(note_id)
        with self.connection() as connection:
            row = connection.execute("SELECT id,title,body,created_at FROM notes WHERE id=?", (note_id,)).fetchone()
            if row is None:
                raise ValueError("Nota nao encontrada")
            return dict(row)

    def search(self, query, limit=20):
        query = text(query, 200, "Busca")
        bounded_limit(limit)
        with self.connection() as connection:
            rows = connection.execute("SELECT id,title,body,created_at FROM notes WHERE instr(lower(title),lower(?))>0 OR instr(lower(body),lower(?))>0 ORDER BY id DESC LIMIT ?", (query, query, limit)).fetchall()
            return [dict(row) for row in rows]

    def update(self, note_id, title=None, body=None):
        positive_id(note_id)
        if title is None and body is None:
            raise ValueError("Informe titulo ou texto para editar")
        if title is not None:
            title = text(title, 200, "Titulo")
        if body is not None:
            body = text(body, 10000, "Texto", required=False)
        with self.connection() as connection:
            row = connection.execute("SELECT title,body FROM notes WHERE id=?", (note_id,)).fetchone()
            if row is None:
                raise ValueError("Nota nao encontrada")
            connection.execute("UPDATE notes SET title=?,body=? WHERE id=?", (title if title is not None else row["title"], body if body is not None else row["body"], note_id))
        return self.get(note_id)

    def delete(self, note_id, confirm=False):
        positive_id(note_id)
        if confirm is not True:
            raise ValueError("Exclusao exige confirmacao explicita")
        with self.connection() as connection:
            cursor = connection.execute("DELETE FROM notes WHERE id=?", (note_id,))
            if cursor.rowcount != 1:
                raise ValueError("Nota nao encontrada")
        return {"id": note_id, "status": "deleted"}

    def export(self, name):
        name = filename(name, ".json")
        with self.connection() as connection:
            rows = connection.execute("SELECT id,title,body,created_at FROM notes ORDER BY id LIMIT 10001").fetchall()
        if len(rows) > 10000:
            raise ValueError("Exportacao limitada a 10000 notas; use backup SQLite")
        payload = {"schema": 1, "encrypted": False, "notes": [dict(row) for row in rows]}
        relative = "Database_Nexus/exports/" + name
        if not self.engine._write_new(relative, json.dumps(payload, ensure_ascii=False, indent=2) + "\n"):
            raise FileExistsError("Exportacao existente; escolha outro nome")
        return {"path": str(self.engine.path(relative)), "count": len(rows), "encrypted": False}


class Tasks(LocalStore):
    @contextmanager
    def connection(self):
        with super().connection() as connection:
            connection.execute("CREATE TABLE IF NOT EXISTS tasks (id INTEGER PRIMARY KEY, title TEXT NOT NULL, done INTEGER NOT NULL DEFAULT 0 CHECK(done IN (0,1)), created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)")
            yield connection

    def add(self, title):
        title = text(title, 200, "Titulo")
        with self.connection() as connection:
            cursor = connection.execute("INSERT INTO tasks(title) VALUES (?)", (title,))
            return {"id": cursor.lastrowid, "title": title, "done": False}

    def list(self, state="open", limit=20):
        if state not in ("open", "done", "all"):
            raise ValueError("Estado deve ser open, done ou all")
        bounded_limit(limit)
        with self.connection() as connection:
            if state == "all":
                rows = connection.execute("SELECT * FROM tasks ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
            else:
                rows = connection.execute("SELECT * FROM tasks WHERE done=? ORDER BY id DESC LIMIT ?", (int(state == "done"), limit)).fetchall()
            return [dict(row) for row in rows]

    def set_done(self, task_id, done=True):
        positive_id(task_id)
        if type(done) is not bool:
            raise ValueError("Estado deve ser booleano")
        with self.connection() as connection:
            cursor = connection.execute("UPDATE tasks SET done=? WHERE id=?", (int(done), task_id))
            if cursor.rowcount != 1:
                raise ValueError("Tarefa nao encontrada")
        return {"id": task_id, "done": done}


class Database(LocalStore):
    def check(self):
        with self.connection() as connection:
            results = [row[0] for row in connection.execute("PRAGMA quick_check").fetchall()]
            notes = connection.execute("SELECT count(*) FROM notes").fetchone()[0]
        return {"ok": results == ["ok"], "integrity": results, "notes": notes, "encrypted": False}

    def backup(self, name):
        name = filename(name, ".sqlite3")
        relative = "Database_Nexus/backups/" + name
        self.engine.setup_structure()
        if not self.engine._write_new(relative, ""):
            raise FileExistsError("Backup existente; escolha outro nome")
        destination = self.engine.path(relative)
        try:
            with self.connection() as source:
                target = sqlite3.connect(str(destination))
                try:
                    source.backup(target)
                    integrity = target.execute("PRAGMA quick_check").fetchone()[0]
                    if integrity != "ok":
                        raise RuntimeError("Backup nao passou na verificacao")
                finally:
                    target.close()
        except Exception:
            # Remove somente o arquivo novo criado por esta chamada, nunca um backup anterior.
            destination.unlink(missing_ok=True)
            raise
        return {"path": str(destination), "status": "backup_verified", "encrypted": False}
