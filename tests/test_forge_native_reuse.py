"""Synthetic Android/Termux regression; not a device compatibility test."""
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from official_core import forge_archives as archives


class NativeReuseTests(unittest.TestCase):
    def test_native_plan_revalidates_original_directory_without_network_or_writes(self):
        with tempfile.TemporaryDirectory() as folder:
            base = Path(folder).resolve()
            directory = base / "private-bin"
            native = str(base / "system-rg")
            for platform in ("termux-aarch64", "android-aarch64"):
                with self.subTest(platform=platform), patch.object(archives, "platform_key", return_value=platform), patch.object(archives.shutil, "which", return_value=native), patch.object(archives, "build_opener") as network:
                    item = archives.plan("rg", directory)
                    self.assertEqual(item["directory"], str(directory))
                    result = archives.install_planned(item)
                    self.assertEqual(result, item)
                    self.assertEqual(result["status"], "system_available")
                    self.assertFalse(result["downloaded"])
                    self.assertFalse(directory.exists())
                    network.assert_not_called()

    def test_missing_native_tool_is_rejected_without_linux_fallback(self):
        with tempfile.TemporaryDirectory() as folder:
            directory = Path(folder).resolve() / "absent"
            for platform in ("termux-aarch64", "android-aarch64"):
                with self.subTest(platform=platform), patch.object(archives, "platform_key", return_value=platform), patch.object(archives.shutil, "which", return_value=None), patch.object(archives, "build_opener") as network:
                    with self.assertRaises(ValueError):
                        archives.plan("rg", directory)
                    self.assertFalse(directory.exists())
                    network.assert_not_called()


if __name__ == "__main__":
    unittest.main()
