# SPDX-License-Identifier: MIT
"""Bounded Linux endurance and actual SIGKILL recovery; synthetic data only."""
import argparse
import json
import os
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from official_core.engine import MasterEngine
from official_core.services import Notes, Tasks, Database


def rss():
    for line in Path("/proc/self/status").read_text().splitlines():
        if line.startswith("VmRSS:"):
            return int(line.split()[1]) * 1024
    raise RuntimeError("Linux RSS unavailable")


def child(mode, root, ready):
    engine = MasterEngine(root)
    if mode == "transaction":
        con = sqlite3.connect(str(engine.path("Database_Nexus/notes.sqlite3")))
        con.execute("PRAGMA cache_size=10")
        con.execute("BEGIN IMMEDIATE")
        con.execute("UPDATE notes SET body=? WHERE title= ?", ("y" * 8000, "seed"))
        con.execute("INSERT INTO notes(title,body) VALUES (?,?)", ("uncommitted", "must vanish"))
        Path(ready).write_text("transaction-open")
    else:
        original = os.link
        def barrier(source, target):
            if mode == "after-publish":
                original(source, target)
            Path(ready).write_text(mode)
            while True:
                time.sleep(1)
        os.link = barrier
        engine._write_new("Gaming_Environment/probe.json", json.dumps({"complete": True}) + "\n")
    while True:
        time.sleep(1)


def kill_at_barrier(mode, root, base):
    ready = base / (mode + "-ready")
    proc = subprocess.Popen([sys.executable, __file__, "--child", mode, "--root", str(root), "--ready", str(ready)], stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    try:
        deadline = time.monotonic() + 30
        while not ready.exists():
            if proc.poll() is not None:
                raise RuntimeError("Child failed before barrier: " + proc.stderr.read().decode()[-1000:])
            if time.monotonic() > deadline:
                raise TimeoutError("Child barrier timeout")
            time.sleep(0.02)
        proc.kill()
        proc.wait(timeout=10)
        assert proc.returncode == -9, "Expected real SIGKILL on Linux"
    finally:
        if proc.poll() is None:
            proc.kill()
            proc.wait(timeout=10)
        proc.stderr.close()


def recovery(base):
    root = base / "recovery-db"
    engine = MasterEngine(root)
    sentinel = engine.add_note("sentinel", "preserved")["id"]
    con = engine._database()
    try:
        con.executemany("INSERT INTO notes(title,body) VALUES (?,?)", [("seed", "x" * 4096)] * 256)
        con.commit()
    finally:
        con.close()
    kill_at_barrier("transaction", root, base)
    journal = engine.path("Database_Nexus/notes.sqlite3-journal")
    assert journal.is_file() and journal.stat().st_size > 512, "Expected journal from interrupted write"
    journal_bytes = journal.stat().st_size
    restarted = MasterEngine(root)
    check = Database(restarted).check()
    assert check["ok"] and check["notes"] == 257, check
    assert Notes(restarted).get(sentinel)["body"] == "preserved"
    con = restarted._database()
    try:
        assert con.execute("SELECT count(*) FROM notes WHERE title= ? AND body= ?", ("seed", "x" * 4096)).fetchone()[0] == 256
        assert con.execute("SELECT count(*) FROM notes WHERE title= ?", ("uncommitted",)).fetchone()[0] == 0
        assert con.execute("PRAGMA integrity_check").fetchall() == [("ok",)]
    finally:
        con.close()
    files = []
    for mode in ("before-publish", "after-publish"):
        root = base / mode
        engine = MasterEngine(root)
        engine.setup_structure()
        kill_at_barrier(mode, root, base)
        target = engine.path("Gaming_Environment/probe.json")
        exists = target.exists()
        assert exists == (mode == "after-publish")
        if exists:
            assert json.loads(target.read_text()) == {"complete": True}
        residual = len(list(root.rglob(".rpa-write-*")))
        new_engine = MasterEngine(root)
        new_engine.setup_structure()
        created = new_engine._write_new("Gaming_Environment/probe.json", json.dumps({"complete": True}) + "\n")
        assert created == (mode == "before-publish")
        assert json.loads(target.read_text()) == {"complete": True}
        files.append({"stage": mode, "partial_target_exposed": False, "restart_verified": True, "orphaned_staging_files_after_sigkill": residual})
    return {"sigkill_cases": 3, "sqlite_rollback_verified": True, "journal_bytes_before_recovery": journal_bytes, "committed_rows_preserved": 257, "file_publication": files, "power_loss_simulated": False}


def endurance(base, seconds):
    engine = MasterEngine(base / "endurance")
    notes, tasks = Notes(engine), Tasks(engine)
    engine.setup_structure()
    start = time.monotonic()
    cycles = 0
    samples = []
    next_sample = 0
    while time.monotonic() - start < seconds:
        note = engine.add_note("synthetic endurance", "x" * 1024)["id"]
        assert notes.update(note, body="updated")["body"] == "updated"
        assert notes.get(note)["id"] == note
        assert notes.search("endurance", 1)
        task = tasks.add("synthetic task")["id"]
        assert tasks.set_done(task, True)["done"]
        assert tasks.list("done", 1)[0]["id"] == task
        assert engine.list_notes(1)[0]["id"] == note
        elapsed = time.monotonic() - start
        if elapsed >= next_sample:
            samples.append({"seconds": round(elapsed, 3), "rss_bytes": rss(), "cycles": cycles + 1})
            next_sample = elapsed + 1
        cycles += 1
        time.sleep(0.01)
    elapsed = time.monotonic() - start
    warm = [s["rss_bytes"] for s in samples if s["seconds"] >= min(15, seconds / 4)]
    assert len(warm) >= 2 and cycles >= 20, "Insufficient workload"
    growth = max(warm) - min(warm)
    peak = max(s["rss_bytes"] for s in samples)
    check = Database(MasterEngine(engine.base_dir)).check()
    assert check["ok"] and check["notes"] == cycles, check
    assert growth <= 32 * 1024 * 1024, "RSS growth exceeded 32 MiB"
    assert peak <= 256 * 1024 * 1024, "RSS peak exceeded 256 MiB"
    return {"requested_seconds": seconds, "elapsed_seconds": round(elapsed, 3), "cycles": cycles, "service_operations": cycles * 8, "rss_peak_bytes": peak, "rss_after_warmup_range_bytes": growth, "growth_limit_bytes": 32 * 1024 * 1024, "database_reopened_and_verified": True, "rss_samples": samples, "scope": "Python local services only, not model/browser RSS or multi-hour soak"}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--seconds", type=int, default=300)
    parser.add_argument("--child", choices=["transaction", "before-publish", "after-publish"])
    parser.add_argument("--root")
    parser.add_argument("--ready")
    args = parser.parse_args()
    if args.child:
        return child(args.child, args.root, args.ready)
    if not 30 <= args.seconds <= 600:
        parser.error("seconds must be 30..600")
    evidence = {"android_device_tested": False, "passed": False}
    try:
        with tempfile.TemporaryDirectory(prefix="rpa-extended-") as directory:
            base = Path(directory).resolve()
            evidence["recovery"] = recovery(base)
            evidence["endurance"] = endurance(base, args.seconds)
        evidence["passed"] = True
    except Exception as error:
        evidence["error"] = {"type": type(error).__name__, "message": str(error)[:2000]}
    Path("endurance-evidence.json").write_text(json.dumps(evidence, indent=2) + "\n")
    summary = dict(evidence)
    if "endurance" in summary:
        summary["endurance"] = {k: v for k, v in summary["endurance"].items() if k != "rss_samples"}
    print(json.dumps(summary, indent=2), flush=True)
    return 0 if evidence["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
