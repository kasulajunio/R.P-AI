# SPDX-License-Identifier: MIT
"""System identification must not invoke OS commands, even without a platform cache."""
import unittest
from unittest.mock import patch
from official_core.bootstrap import detect_system


class SystemDetectionTests(unittest.TestCase):
    def test_native_platform_without_subprocess_or_platform_probe(self):
        cases = {"win32": "windows", "linux": "linux", "darwin": "macos", "android": "android", "freebsd14": "unsupported"}
        with patch("platform.system", side_effect=AssertionError("No platform probe")), patch("subprocess.Popen", side_effect=AssertionError("No subprocess")):
            for native, expected in cases.items():
                with self.subTest(platform=native), patch("official_core.bootstrap.sys.platform", native):
                    self.assertEqual(detect_system(environ={}), expected)

    def test_explicit_system_override_is_preserved(self):
        with patch("official_core.bootstrap.sys.platform", "win32"):
            self.assertEqual(detect_system("Linux", {}), "linux")
            self.assertEqual(detect_system("Darwin", {}), "macos")
            self.assertEqual(detect_system("Windows", {}), "windows")

    def test_android_and_termux_environment_precedence(self):
        with patch("official_core.bootstrap.sys.platform", "linux"):
            self.assertEqual(detect_system(environ={"ANDROID_ROOT": "/system"}), "android")
            self.assertEqual(detect_system(environ={"TERMUX_VERSION": "synthetic", "ANDROID_ROOT": "/system"}), "termux")
            self.assertEqual(detect_system(environ={"PREFIX": "/data/data/com.termux/files/usr"}), "termux")


if __name__ == "__main__":
    unittest.main()
