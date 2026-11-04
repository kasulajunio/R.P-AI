# SPDX-License-Identifier: MIT
"""Natural-language punctuation is not part of an unquoted requested ID."""
import unittest
from official_core.app_contract import requested_ids, violations


class ContractPunctuationTests(unittest.TestCase):
    def test_sentence_full_stop_is_not_an_id_character(self):
        for prompt in ["output id=value. Next sentence.", "output id=value.", "output id=value, followed by explanation.", "output id=value; next instruction"]:
            with self.subTest(prompt=prompt):
                self.assertEqual(requested_ids(prompt), {"value": "output"})
                self.assertEqual(violations("<output id=value></output>", requested_ids(prompt)), [])

    def test_dots_inside_identifier_are_preserved(self):
        self.assertEqual(requested_ids("output id=app.value. Next."), {"app.value": "output"})

    def test_quoted_identifier_is_always_literal(self):
        for quote in [chr(34), chr(39)]:
            self.assertEqual(requested_ids("output id=" + quote + "value." + quote + "."), {"value.": "output"})

    def test_explicit_html_unquoted_attribute_is_literal(self):
        self.assertEqual(requested_ids("Use <output id=value.>0</output>."), {"value.": "output"})

    def test_sentence_fix_does_not_accept_wrong_id(self):
        requirements = requested_ids("output id=value.")
        self.assertTrue(violations("<output id=counter>0</output>", requirements))
        self.assertTrue(violations("<output id=value.>0</output>", requirements))


if __name__ == "__main__":
    unittest.main()
