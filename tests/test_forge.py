import contextlib
import hashlib
import io
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import MagicMock, patch
from official_core.forge import Asset, ApprovedRedirect, CATALOG, Forge, check_url, main, platform_key


class Response(io.BytesIO):
    def geturl(self):
        return "https://release-assets.githubusercontent.com/example"


class ForgeTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.directory = Path(self.tmp.name).resolve() / "bin"
        self.payload = b"\x7fELFunit-test-not-executable"
        self.key = "linux-glibc-x86_64"
        self.asset = Asset("https://github.com/example/tool/releases/download/v1/tool", hashlib.sha256(self.payload).hexdigest(), "v1")
        self.forge = Forge(self.directory, {"tool": {self.key: self.asset}})
        self.which = patch("official_core.forge.shutil.which", return_value=None).start()
        self.addCleanup(patch.stopall)
        patch("official_core.forge.platform_key", return_value=self.key).start()
        self.opener = patch("official_core.forge.build_opener").start()
        self.opener.return_value.open.side_effect = lambda *a, **k: Response(self.payload)

    def test_plan_has_no_network_or_writes(self):
        result = self.forge.ensure("tool")
        self.assertEqual(result["status"], "download_required")
        self.assertFalse(self.directory.exists())
        self.opener.assert_not_called()

    def test_install_checks_hash_and_preserves_global_path(self):
        old = os.environ.get("PATH")
        result = self.forge.ensure("tool", install=True)
        self.assertEqual(Path(result["path"]).read_bytes(), self.payload)
        self.assertTrue(result["downloaded"])
        self.assertEqual(os.environ.get("PATH"), old)

    def test_second_install_reuses_verified_binary(self):
        self.forge.ensure("tool", install=True)
        self.assertEqual(self.forge.ensure("tool", install=True)["status"], "verified")
        self.assertEqual(self.opener.return_value.open.call_count, 1)

    def test_checksum_mismatch_cleans_temporary_file(self):
        self.opener.return_value.open.side_effect = lambda *a, **k: Response(b"malicious")
        with self.assertRaises(ValueError):
            self.forge.ensure("tool", install=True)
        self.assertEqual(list(self.directory.iterdir()), [])

    def test_tampered_existing_is_not_replaced(self):
        result = self.forge.ensure("tool", install=True)
        target = Path(result["path"])
        target.write_bytes(b"preserve evidence")
        with self.assertRaises(ValueError):
            self.forge.ensure("tool", install=True)
        self.assertEqual(target.read_bytes(), b"preserve evidence")

    def test_archive_or_script_rejected_even_with_matching_hash(self):
        for content in (b"#!/bin/sh\necho unsafe", b"PKzip", b"<html>"):
            with self.subTest(content=content):
                asset = Asset(self.asset.url, hashlib.sha256(content).hexdigest(), "v1")
                forge = Forge(self.directory, {"tool": {self.key: asset}})
                self.opener.return_value.open.side_effect = lambda *a, **k: Response(content)
                with self.assertRaises(ValueError):
                    forge.ensure("tool", install=True)

    def test_size_cap(self):
        with patch("official_core.forge.MAX_BYTES", 2), self.assertRaises(ValueError):
            self.forge.ensure("tool", install=True)
        self.assertEqual(list(self.directory.iterdir()), [])

    def test_unknown_and_traversal_rejected(self):
        for tool in ("unknown", "../tool", "tool; rm", "/bin/tool"):
            with self.subTest(tool=tool), self.assertRaises(ValueError):
                self.forge.ensure(tool, install=True)
        self.opener.assert_not_called()

    def test_abi_mismatch_never_downloads(self):
        with patch("official_core.forge.platform_key", return_value="termux-aarch64"), self.assertRaises(ValueError):
            self.forge.ensure("tool", install=True)
        self.opener.assert_not_called()

    def test_existing_system_tool_is_not_repaired(self):
        self.which.return_value = "/existing/tool"
        self.assertEqual(self.forge.ensure("tool", install=True)["status"], "system_available")
        self.opener.assert_not_called()

    def test_run_does_not_download_without_authorization(self):
        with self.assertRaises(FileNotFoundError):
            self.forge.run(["tool", "--version"])
        self.opener.assert_not_called()

    def test_failed_command_is_not_retried_or_downloaded(self):
        self.which.return_value = "/existing/tool"
        with patch("official_core.forge.subprocess.run", return_value=subprocess.CompletedProcess([], 9)) as run:
            self.assertEqual(self.forge.run(["tool"], repair=True).returncode, 9)
        run.assert_called_once()
        self.opener.assert_not_called()

    def test_missing_exec_permission_is_not_repaired(self):
        self.which.return_value = "/existing/tool"
        with patch("official_core.forge.subprocess.run", side_effect=PermissionError), self.assertRaises(PermissionError):
            self.forge.run(["tool"], repair=True)
        self.opener.assert_not_called()

    def test_run_has_no_shell_or_global_environment_change(self):
        self.which.return_value = "/existing/tool"
        old = os.environ.copy()
        with patch("official_core.forge.subprocess.run") as run:
            self.forge.run(["tool", "; not a shell command"])
        self.assertFalse(run.call_args.kwargs["shell"])
        self.assertEqual(os.environ, old)

    def test_unsafe_urls_rejected(self):
        for url in ("http://github.com/x", "https://evil.example/x", "https://github.com.evil.example/x", "https://user:secret@github.com/x", "https://github.com:8443/x"):
            with self.subTest(url=url), self.assertRaises(ValueError):
                check_url(url)

    def test_redirect_rejects_http_and_unknown_host(self):
        from urllib.request import Request
        request = Request(self.asset.url)
        for url in ("http://github.com/x", "https://evil.example/x"):
            with self.assertRaises(ValueError):
                ApprovedRedirect().redirect_request(request, None, 302, "Found", {}, url)

    def test_release_pins_are_valid(self):
        for variants in CATALOG.values():
            for asset in variants.values():
                asset.validate()

    def test_no_install_without_network_flag(self):
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as result:
            main(["install", "jq"])
        self.assertEqual(result.exception.code, 2)
        self.opener.assert_not_called()

    @unittest.skipIf(os.name == "nt", "Criacao de symlink pode exigir privilegio no Windows")
    def test_destination_symlink_rejected(self):
        real = self.directory.parent / "elsewhere"
        real.mkdir()
        self.directory.symlink_to(real, target_is_directory=True)
        with self.assertRaises(ValueError):
            self.forge.ensure("tool", install=True)
        self.assertEqual(list(real.iterdir()), [])


if __name__ == "__main__":
    unittest.main()
