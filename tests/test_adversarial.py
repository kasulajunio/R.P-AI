# SPDX-License-Identifier: MIT
"""Bounded, reproducible offline adversarial checks. Synthetic faults are explicit."""
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager, closing
import errno
import io
import json
import os
from pathlib import Path
import random
import sqlite3
import tarfile
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch
import zipfile

from official_core.engine import MasterEngine, SafetyError
from official_core.services import Notes, Tasks, Database, positive_id
from official_core.assistant_cli import create_app
from official_core.console import status
from official_core import local_ai
from official_core.forge import check_url
from official_core.forge_archives import copy_selected, check_binary


class AdversarialTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name).resolve()
        self.engine = MasterEngine(self.base / "workspace")

    def test_6000_seeded_path_escape_attempts(self):
        rng = random.Random(20261103)
        for index in range(3000):
            name = "".join(rng.choice("abcdef0123456789") for _ in range(12))
            for candidate in [name + "/../escape", name + "/" + rng.choice(["CON.txt", "AUX.json", "NUL", "a:b", "a\\b", "..", ".", "end.", "bad\x00name"])]:
                with self.subTest(case=index, path=candidate), self.assertRaises(SafetyError):
                    self.engine.path(candidate)
        self.assertFalse(self.engine.base_dir.exists())

    def test_3000_invalid_app_names_never_write(self):
        for index in range(1000):
            for name in ["../app-" + str(index), "Bad-" + str(index), "app/" + str(index)]:
                with self.assertRaises(ValueError):
                    create_app(self.engine.base_dir, name)
        self.assertFalse(self.engine.base_dir.exists())

    def test_concurrent_new_file_has_one_complete_winner(self):
        messages = [(str(i) + "x") * 50000 for i in range(24)]
        with ThreadPoolExecutor(max_workers=8) as pool:
            results = list(pool.map(lambda s: self.engine._write_new("race.txt", s), messages))
        self.assertEqual(sum(results), 1)
        winner = messages[results.index(True)]
        self.assertEqual(self.engine.path("race.txt").read_text(encoding="utf-8"), winner)
        self.assertFalse(list(self.engine.base_dir.glob(".rpa-write-*")))

    def test_simulated_disk_full_leaves_no_partial_destination(self):
        original = os.fdopen
        @contextmanager
        def broken_fdopen(fd, *args, **kwargs):
            with original(fd, *args, **kwargs) as stream:
                class Broken:
                    def write(self, value):
                        stream.write(value[:5])
                        stream.flush()
                        raise OSError(errno.ENOSPC, "synthetic disk full")
                yield Broken()
        with patch("official_core.engine.os.fdopen", broken_fdopen):
            with self.assertRaises(OSError):
                self.engine._write_new("atomic.json", "{\"complete\":true}")
        self.assertFalse(self.engine.path("atomic.json").exists())
        self.assertFalse(list(self.engine.base_dir.glob(".rpa-write-*")))
        self.assertTrue(self.engine._write_new("atomic.json", "{}"))

    def test_invalid_unicode_leaves_no_partial_destination(self):
        with self.assertRaises(UnicodeError):
            self.engine._write_new("invalid.txt", "\ud800")
        self.assertFalse(self.engine.path("invalid.txt").exists())
        self.assertTrue(self.engine._write_new("invalid.txt", "recovered"))

    def test_80_concurrent_sqlite_writes_are_unique_and_persistent(self):
        self.engine.setup_structure()
        with ThreadPoolExecutor(max_workers=8) as pool:
            items = list(pool.map(lambda i: self.engine.add_note("note-" + str(i), "body-" + str(i)), range(80)))
        self.assertEqual(len({x["id"] for x in items}), 80)
        reopened = MasterEngine(self.engine.base_dir)
        self.assertEqual(len(reopened.list_notes(100)), 80)
        self.assertTrue(Database(reopened).check()["ok"])

    def test_failed_transaction_rolls_back(self):
        store = Notes(self.engine)
        with self.assertRaises(RuntimeError):
            with store.connection() as connection:
                connection.execute("INSERT INTO notes(title,body) VALUES (?,?)", ("rollback", "not committed"))
                raise RuntimeError("synthetic application crash")
        self.assertEqual(self.engine.list_notes(), [])

    def test_backup_is_independent_consistent_and_not_overwritten(self):
        for i in range(128):
            self.engine.add_note("note-" + str(i), "body")
        result = Database(self.engine).backup("snapshot.sqlite3")
        snapshot = Path(result["path"])
        with closing(sqlite3.connect(snapshot)) as db:
            self.assertEqual(db.execute("PRAGMA integrity_check").fetchone()[0], "ok")
            self.assertEqual(db.execute("SELECT count(*) FROM notes").fetchone()[0], 128)
        original = snapshot.read_bytes()
        self.engine.add_note("after snapshot")
        with self.assertRaises(FileExistsError):
            Database(self.engine).backup("snapshot.sqlite3")
        self.assertEqual(snapshot.read_bytes(), original)

    def test_sql_metacharacters_remain_data(self):
        values = ["x'); DROP TABLE notes;--", "%_\\", "<script>alert(1)</script>", "nota com acento: ação 漢字 😀"]
        for value in values:
            item = self.engine.add_note(value, value)
            self.assertEqual(Notes(self.engine).get(item["id"])["body"], value)
            self.assertEqual(Notes(self.engine).search(value)[0]["id"], item["id"])
        self.assertTrue(Database(self.engine).check()["ok"])

    def test_sqlite_id_bounds_rejected_before_database(self):
        for value in [True, False, 0, -1, 1.5, "1", None, 2**63, 10**100]:
            with self.subTest(value=value), self.assertRaises(ValueError):
                positive_id(value)
        self.assertEqual(positive_id(2**63 - 1), 2**63 - 1)

    def test_offline_operations_never_open_network_or_subprocess(self):
        with patch("socket.create_connection", side_effect=AssertionError("network forbidden")), patch("urllib.request.OpenerDirector.open", side_effect=AssertionError("HTTP forbidden")), patch("subprocess.Popen", side_effect=AssertionError("process forbidden")):
            self.engine.setup_structure()
            self.engine.add_note("offline")
            task = Tasks(self.engine).add("offline task")
            Tasks(self.engine).set_done(task["id"])
            create_app(self.engine.base_dir, "offline-counter")
            self.assertTrue(status(self.engine.base_dir, self.base)["database"]["ok"])

    def test_control_characters_never_normalized_into_download_url(self):
        clean = "https://github.com/a/b/releases/download/v1/file"
        for character in ["\n", "\r", "\t", "\x00", "\x1f", "\x7f"]:
            for value in [character + clean, clean.replace("github.com", "git" + character + "hub.com")]:
                with self.subTest(url=repr(value)), self.assertRaises(ValueError):
                    check_url(value, initial=True)

    def test_forged_binary_headers_rejected(self):
        binary = self.base / "binary"
        for content in [b"", b"#!/bin/sh\necho bad", b"MZ" + bytes(100), b"\x7fELF" + bytes(60)]:
            binary.write_bytes(content)
            for key in ["linux-glibc-x86_64", "darwin-aarch64", "windows-x86_64"]:
                with self.assertRaises(ValueError):
                    check_binary(binary, key)

    def test_80_tar_zip_traversal_archives_never_extract(self):
        header = bytearray(64)
        header[:6] = b"\x7fELF\x02\x01"
        header[18:20] = (62).to_bytes(2, "little")
        for index in range(40):
            for fmt in ["tar.gz", "zip"]:
                package = self.base / (str(index) + "." + fmt)
                destination = self.base / ("out-" + str(index) + "-" + fmt)
                bad = "pkg/../escape-" + str(index)
                if fmt == "zip":
                    with zipfile.ZipFile(package, "w") as archive:
                        archive.writestr("pkg/tool", header)
                        archive.writestr(bad, b"bad")
                else:
                    with tarfile.open(package, "w:gz") as archive:
                        member = tarfile.TarInfo("pkg/tool")
                        member.size = len(header)
                        archive.addfile(member, io.BytesIO(header))
                        member = tarfile.TarInfo(bad)
                        member.size = 3
                        archive.addfile(member, io.BytesIO(b"bad"))
                with self.assertRaises(ValueError):
                    copy_selected(package, destination, "pkg/tool", "linux-glibc-x86_64", fmt)
                self.assertFalse(destination.exists())
                self.assertFalse((self.base / ("escape-" + str(index))).exists())

    def test_invalid_unicode_prompt_is_controlled_before_http(self):
        with patch.object(local_ai, "build_opener", side_effect=AssertionError("HTTP forbidden")):
            with self.assertRaises(local_ai.LocalAIError):
                local_ai.chat([{"role": "user", "content": "\ud800"}])

    def test_boolean_timeout_is_not_a_number(self):
        with patch.object(local_ai, "build_opener", side_effect=AssertionError("HTTP forbidden")):
            with self.assertRaises(local_ai.LocalAIError):
                local_ai.chat([{"role": "user", "content": "hello"}], timeout=True)

    def test_deep_json_and_invalid_unicode_response_fail_safely(self):
        payloads = [b"[" * 2000 + b"0" + b"]" * 2000, b"{\"done\":true,\"message\":{\"role\":\"assistant\",\"content\":\"\\ud800\"}}"]
        for payload in payloads:
            opener = SimpleNamespace(open=lambda *args, **kwargs: io.BytesIO(payload))
            with patch.object(local_ai, "build_opener", return_value=opener):
                with self.assertRaises(local_ai.LocalAIError):
                    local_ai.chat([{"role": "user", "content": "hello"}])


if __name__ == "__main__":
    unittest.main()
