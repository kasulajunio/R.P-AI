import unittest
from scripts.check_secrets import REVIEWED_FIXTURES, findings_for_blob


class ScannerFixtureTests(unittest.TestCase):
    def setUp(self):
        (self.blob, self.rule), self.fixture = next(iter(REVIEWED_FIXTURES.items()))

    def test_reviewed_synthetic_match_only(self):
        self.assertEqual(findings_for_blob(self.blob, self.fixture), [])

    def test_same_fixture_new_blob_still_blocked(self):
        self.assertEqual(findings_for_blob("0" * 40, self.fixture), [("0" * 40, self.rule)])

    def test_other_url_in_same_blob_blocked(self):
        other = b"https://" + b"different" + b":password@"
        self.assertEqual(findings_for_blob(self.blob, self.fixture + b"\n" + other), [(self.blob, self.rule)])

    def test_other_rule_in_same_blob_blocked(self):
        token = b"ghp" + b"_" + b"x" * 40
        self.assertEqual(findings_for_blob(self.blob, self.fixture + b"\n" + token), [(self.blob, "github_token")])


if __name__ == "__main__":
    unittest.main()
