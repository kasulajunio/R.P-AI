"""ABI regression fixtures; not an Android device test."""
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from official_core import forge, forge_archives


class LibcDetectionTests(unittest.TestCase):
    def test_linux_libc_detection_without_abi_fallback(self):
        cases = [
            (("", ""), "x86_64-alpine-linux-musl", "linux-musl-x86_64"),
            (("", ""), "x86_64-unknown-linux-musl", "linux-musl-x86_64"),
            (("musl", "1.2"), None, "linux-musl-x86_64"),
            (("glibc", "2.36"), "x86_64-alpine-linux-musl", "linux-glibc-x86_64"),
            (("", ""), None, "linux-unknown-x86_64"),
            (("", ""), "x86_64-linux-gnu", "linux-unknown-x86_64"),
            (("", ""), "musl-untrusted-label", "linux-unknown-x86_64"),
        ]
        for libc, target, expected in cases:
            with self.subTest(libc=libc, target=target), patch.dict(os.environ, {}, clear=True), patch.object(forge.platform, "system", return_value="Linux"), patch.object(forge.platform, "machine", return_value="x86_64"), patch.object(forge.platform, "libc_ver", return_value=libc), patch.object(forge.sysconfig, "get_config_var", return_value=target):
                self.assertEqual(forge.platform_key(), expected)

    def test_musl_catalog_plan_is_offline(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder).resolve() / "absent"
            with patch.object(forge_archives, "platform_key", return_value="linux-musl-x86_64"), patch.object(forge_archives, "build_opener") as network:
                for tool in ("rg", "fd"):
                    item = forge_archives.plan(tool, root)
                    self.assertEqual(item["status"], "download_required")
                    self.assertIn("linux-musl", item["url"])
                    self.assertFalse(item["downloaded"])
                network.assert_not_called()
                self.assertFalse(root.exists())


if __name__ == "__main__":
    unittest.main()
