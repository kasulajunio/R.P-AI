import contextlib
import io
import json
import sqlite3
import tempfile
import unittest
from pathlib import Path
from official_core.engine import MasterEngine
from official_core.services import Notes, Tasks, Database, positive_id, bounded_limit, filename
from official_core.cli import main


class ServiceTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name).resolve() / "workspace"
        self.engine = MasterEngine(self.root)
        self.notes = Notes(self.engine)
        self.tasks = Tasks(self.engine)

    def add(self, title="Plano", body="Teste local"):
        return self.engine.add_note(title, body)["id"]

    def test_get_and_missing(self):
        note_id = self.add()
        self.assertEqual(self.notes.get(note_id)["title"], "Plano")
        with self.assertRaises(ValueError):
            self.notes.get(999)

    def test_search_and_sql_input(self):
        self.add("Plano", "contabilidade local")
        self.assertEqual(len(self.notes.search("contabilidade")), 1)
        self.assertEqual(self.notes.search("nonexistent"), [])
        self.assertEqual(self.notes.search("\"; DROP TABLE notes;--"), [])
        self.assertEqual(len(self.engine.list_notes()), 1)

    def test_update_preserves_unspecified_values(self):
        note_id = self.add()
        self.assertEqual(self.notes.update(note_id, title="Novo")["body"], "Teste local")
        self.assertEqual(self.notes.update(note_id, body="")["title"], "Novo")
        with self.assertRaises(ValueError):
            self.notes.update(note_id)
        with self.assertRaises(ValueError):
            self.notes.update(999, title="X")

    def test_delete_requires_confirmation(self):
        note_id = self.add()
        with self.assertRaises(ValueError):
            self.notes.delete(note_id)
        self.assertEqual(self.notes.get(note_id)["id"], note_id)
        self.notes.delete(note_id, confirm=True)
        with self.assertRaises(ValueError):
            self.notes.get(note_id)

    def test_export_and_no_overwrite(self):
        self.add()
        result = self.notes.export("notes.json")
        exported = Path(result["path"])
        payload = json.loads(exported.read_text(encoding="utf-8"))
        self.assertFalse(payload["encrypted"])
        self.assertEqual(len(payload["notes"]), 1)
        before = exported.read_bytes()
        with self.assertRaises(FileExistsError):
            self.notes.export("notes.json")
        self.assertEqual(exported.read_bytes(), before)

    def test_filename_rejects_traversal(self):
        for value in ("../x.json", "/tmp/x.json", "x\\y.json", "x.txt", "", "a" * 90 + ".json"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                filename(value, ".json")

    def test_tasks_lifecycle_and_persistence(self):
        task_id = self.tasks.add("  Testar projeto  ")["id"]
        self.assertEqual(len(Tasks(MasterEngine(self.root)).list()), 1)
        self.tasks.set_done(task_id)
        self.assertEqual(self.tasks.list(), [])
        self.assertEqual(len(self.tasks.list("done")), 1)
        self.tasks.set_done(task_id, False)
        self.assertEqual(len(self.tasks.list("all")), 1)
        with self.assertRaises(ValueError):
            self.tasks.set_done(999)

    def test_tasks_validate(self):
        with self.assertRaises(ValueError):
            self.tasks.add(" " )
        with self.assertRaises(ValueError):
            self.tasks.list("invalid")
        with self.assertRaises(ValueError):
            self.tasks.set_done(1, done=1)

    def test_database_backup_includes_tasks(self):
        self.add()
        self.tasks.add("Revisar")
        result = Database(self.engine).backup("first.sqlite3")
        target = sqlite3.connect(result["path"])
        try:
            self.assertEqual(target.execute("SELECT count(*) FROM notes").fetchone()[0], 1)
            self.assertEqual(target.execute("SELECT count(*) FROM tasks").fetchone()[0], 1)
            self.assertEqual(target.execute("PRAGMA quick_check").fetchone()[0], "ok")
        finally:
            target.close()
        self.assertTrue(Database(self.engine).check()["ok"])
        with self.assertRaises(FileExistsError):
            Database(self.engine).backup("first.sqlite3")

    def test_bounds(self):
        for value in (0, -1, True, "1", None):
            with self.subTest(value=value), self.assertRaises(ValueError):
                positive_id(value)
        for value in (0, 101, True, "1"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                bounded_limit(value)

    def test_cli_commands(self):
        commands = [
            ["note-add", "Plano", "--body", "Texto"],
            ["note-get", "1"],
            ["note-search", "Texto"],
            ["note-update", "1", "--title", "Revisado"],
            ["note-export", "cli.json"],
            ["task-add", "Testar"],
            ["task-list"],
            ["task-done", "1"],
            ["db-check"],
            ["db-backup", "cli.sqlite3"],
            ["note-delete", "1", "--confirm"],
        ]
        for command in commands:
            with self.subTest(command=command), contextlib.redirect_stdout(io.StringIO()) as stream:
                self.assertEqual(main(["--root", str(self.root)] + command), 0)
                json.loads(stream.getvalue())

    def test_cli_rejects_unconfirmed_delete(self):
        self.add()
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(main(["--root", str(self.root), "note-delete", "1"]), 1)
        self.assertEqual(len(self.engine.list_notes()), 1)


if __name__ == "__main__":
    unittest.main()
