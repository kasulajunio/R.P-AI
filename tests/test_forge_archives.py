import contextlib
import hashlib
import io
import os
from pathlib import Path
import tarfile
import tempfile
import unittest
from unittest.mock import patch
from official_core import forge_archives as archives
from official_core.forge import Asset

URL = "https://github.com/example/tool/releases/download/v1/tool.tar.gz"
ELF = b"\x7fELF\x02\x01" + bytes(12) + (183).to_bytes(2, "little") + bytes(44)


def package(entries):
    stream = io.BytesIO()
    with tarfile.open(fileobj=stream, mode="w:gz") as archive:
        for name, payload in entries:
            info = tarfile.TarInfo(name)
            if payload is None:
                info.type = tarfile.SYMTYPE
                info.linkname = "../../outside"
                archive.addfile(info)
            else:
                info.size = len(payload)
                archive.addfile(info, io.BytesIO(payload))
    return stream.getvalue()


class Response(io.BytesIO):
    status = 200
    def geturl(self):
        return URL


@contextlib.contextmanager
def configured(data, digest=None, size=None):
    catalog = {"rg": (Asset(URL, digest or hashlib.sha256(data).hexdigest(), "v1"), len(data) if size is None else size, "pkg/rg")}
    with patch.object(archives, "CATALOG", catalog), patch.object(archives, "platform_key", return_value=archives.PLATFORM), patch.object(archives, "build_opener") as network:
        network.return_value.open.return_value = Response(data)
        yield network


@unittest.skipIf(os.name == "nt", "POSIX permission fixtures; separate ZIP fixtures cover Windows")
class ArchiveTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve() / "bin"
        self.which = patch("official_core.forge_archives.shutil.which", return_value=None)
        self.which.start()
        self.addCleanup(self.which.stop)

    def install(self):
        return archives.batch(["rg"], str(self.root), install=True, allow_network=True)

    def test_exact_binary_installed_without_execution(self):
        data = package([("pkg/rg", ELF)])
        with configured(data), patch("subprocess.run") as execute:
            report = self.install()
        self.assertEqual(report["status"], "complete")
        self.assertEqual((self.root / "rg").read_bytes(), ELF)
        self.assertEqual([p.name for p in self.root.iterdir()], ["rg"])
        execute.assert_not_called()

    def test_plan_is_offline_and_read_only(self):
        with configured(package([("pkg/rg", ELF)])) as network:
            report = archives.batch(["rg"], str(self.root))
            network.assert_not_called()
        self.assertEqual(report["status"], "planned")
        self.assertFalse(self.root.exists())

    def test_consent_required_before_network(self):
        with patch.object(archives, "build_opener") as network, self.assertRaises(PermissionError):
            archives.batch(["rg"], str(self.root), install=True)
        network.assert_not_called()
        self.assertFalse(self.root.exists())

    def test_unsupported_abi_has_no_network(self):
        for platform in ("linux-unknown-x86_64", "termux-aarch64", "android-aarch64", "freebsd-aarch64"):
            with self.subTest(platform=platform), patch.object(archives, "platform_key", return_value=platform), patch.object(archives, "build_opener") as network, self.assertRaises(ValueError):
                self.install()
            network.assert_not_called()
        self.assertFalse(self.root.exists())

    def test_invalid_archives_leave_no_published_binary(self):
        entries = [[("pkg/rg", ELF), ("../outside", b"bad")], [("pkg/rg", ELF), ("/outside", b"bad")], [("pkg/rg", ELF), ("pkg/link", None)], [("pkg/rg", ELF), ("pkg/rg", ELF)], [("pkg/other", ELF)], [("pkg/rg", b"not an ELF binary")]]
        for members in entries:
            with self.subTest(members=members), configured(package(members)):
                report = self.install()
            self.assertEqual(report["status"], "failed")
            self.assertFalse((self.root / "rg").exists())
            self.assertEqual(list(self.root.iterdir()), [])
        self.assertFalse((self.root.parent / "outside").exists())

    def test_bad_hash_and_size_clean_staging(self):
        data = package([("pkg/rg", ELF)])
        for options in ({"digest": "0" * 64}, {"size": len(data) - 1}, {"size": len(data) + 1}):
            with self.subTest(options=options), configured(data, **options):
                self.assertEqual(self.install()["status"], "failed")
            self.assertEqual(list(self.root.iterdir()), [])

    def test_existing_destination_not_overwritten(self):
        self.root.mkdir(mode=0o700)
        target = self.root / "rg"
        target.write_bytes(b"keep")
        with configured(package([("pkg/rg", ELF)])) as network, self.assertRaises(FileExistsError):
            self.install()
        network.assert_not_called()
        self.assertEqual(target.read_bytes(), b"keep")

    def test_unknown_late_item_prevents_all_downloads(self):
        with configured(package([("pkg/rg", ELF)])) as network, self.assertRaises(ValueError):
            archives.batch(["rg", "nmap"], str(self.root), install=True, allow_network=True)
        network.assert_not_called()
        self.assertFalse(self.root.exists())


if __name__ == "__main__":
    unittest.main()
