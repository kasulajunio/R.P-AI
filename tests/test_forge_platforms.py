import io
import os
from pathlib import Path
import stat
import tempfile
import unittest
from unittest.mock import patch
import zipfile
from official_core import forge_archives as archives
from official_core.forge_catalog import CATALOG


def pe(arm=False):
    return b"MZ" + bytes(58) + (64).to_bytes(4, "little") + b"PE\0\0" + (0xAA64 if arm else 0x8664).to_bytes(2, "little") + bytes(64)


class PlatformTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name).resolve()

    def test_all_catalog_entries_are_pinned_and_read_only(self):
        for tool, versions in CATALOG.items():
            for key, (asset, size, member) in versions.items():
                with self.subTest(tool=tool, key=key), patch.object(archives, "platform_key", return_value=key), patch.object(archives, "build_opener") as network:
                    asset.validate()
                    item = archives.plan(tool, self.base / "absent")
                    self.assertEqual(item["size"], size)
                    self.assertEqual(item["member"], member)
                    self.assertTrue(size > 0)
                    self.assertEqual(item["path"].endswith(".exe"), key.startswith("windows-"))
                    network.assert_not_called()
        self.assertFalse((self.base / "absent").exists())

    def test_missing_musl_arm_rg_does_not_use_linux_gnu(self):
        with patch.object(archives, "platform_key", return_value="linux-musl-aarch64"), patch.object(archives, "build_opener") as network, self.assertRaises(ValueError):
            archives.plan("rg", self.base / "bin")
        network.assert_not_called()

    def test_elf_and_macho_architectures(self):
        path = self.base / "binary"
        for key, content in (("linux-glibc-x86_64", b"\x7fELF\x02\x01" + bytes(12) + (62).to_bytes(2, "little") + bytes(44)), ("darwin-x86_64", b"\xcf\xfa\xed\xfe" + (0x1000007).to_bytes(4, "little") + bytes(56)), ("darwin-aarch64", b"\xcf\xfa\xed\xfe" + (0x100000C).to_bytes(4, "little") + bytes(56))):
            path.write_bytes(content)
            archives.check_binary(path, key)
            other = key.rsplit("-", 1)[0] + ("-x86_64" if key.endswith("aarch64") else "-aarch64")
            with self.assertRaises(ValueError):
                archives.check_binary(path, other)

    def test_zip_exact_pe_and_wrong_cpu(self):
        for arm in (False, True):
            package = self.base / "package.zip"
            destination = self.base / ("binary-arm" if arm else "binary-intel")
            with zipfile.ZipFile(package, "w") as archive:
                archive.writestr("pkg/rg.exe", pe(arm))
                archive.writestr("pkg/README", b"safe")
            key = "windows-aarch64" if arm else "windows-x86_64"
            archives.copy_selected(package, destination, "pkg/rg.exe", key, "zip")
            self.assertEqual(destination.read_bytes(), pe(arm))
            with self.assertRaises(ValueError):
                archives.check_binary(destination, "windows-x86_64" if arm else "windows-aarch64")

    def test_zip_rejects_unsafe_members(self):
        bad = ["../escape", "/absolute", "pkg/../escape", "pkg/a:b", "pkg\\escape", "elsewhere/file"]
        for index, name in enumerate(bad):
            package = self.base / (str(index) + ".zip")
            with zipfile.ZipFile(package, "w") as archive:
                archive.writestr("pkg/rg.exe", pe())
                archive.writestr(name, b"bad")
            with self.subTest(name=name), self.assertRaises(ValueError):
                archives.copy_selected(package, self.base / (str(index) + ".exe"), "pkg/rg.exe", "windows-x86_64", "zip")
        self.assertFalse((self.base / "escape").exists())

    def test_zip_symlink_is_rejected(self):
        package = self.base / "links.zip"
        link = zipfile.ZipInfo("pkg/link")
        link.create_system = 3
        link.external_attr = (stat.S_IFLNK | 0o777) << 16
        with zipfile.ZipFile(package, "w") as archive:
            archive.writestr("pkg/rg.exe", pe())
            archive.writestr(link, "../../outside")
        with self.assertRaises(ValueError):
            archives.copy_selected(package, self.base / "binary", "pkg/rg.exe", "windows-x86_64", "zip")

    def test_modified_plan_cannot_authorize_network(self):
        with patch.object(archives, "platform_key", return_value="windows-x86_64"), patch.object(archives, "build_opener") as network:
            item = archives.plan("rg", self.base / "bin")
            item["url"] = "https://github.com/example/other/releases/download/v1/other.zip"
            with self.assertRaises(ValueError):
                archives.install_planned(item)
            network.assert_not_called()

    def test_termux_existing_tools_plan_is_offline(self):
        with patch.object(archives, "platform_key", return_value="termux-aarch64"), patch.object(archives.shutil, "which", return_value=str(self.base / "native-rg")), patch.object(archives, "build_opener") as network:
            item = archives.plan("rg", self.base / "bin")
            self.assertEqual(item["status"], "system_available")
            self.assertFalse(item["downloaded"])
            network.assert_not_called()


if __name__ == "__main__":
    unittest.main()
