# SPDX-License-Identifier: MIT
import unittest
from official_core.app_contract import contract_hint, violations


class ContractTextTests(unittest.TestCase):
    def test_text_and_fallback_markup_is_not_an_existing_control(self):
        for tag in ["textarea", "title", "iframe", "xmp", "noembed", "noframes", "noscript"]:
            with self.subTest(tag=tag):
                document = "<" + tag + "><output id=value>0</output></" + tag + ">"
                self.assertTrue(violations(document, {"value": "output"}))

    def test_textarea_itself_and_controls_after_it_are_valid(self):
        self.assertEqual(violations("<textarea id=text><output id=fake>0</output></textarea><output id=value>0</output>", {"text": "textarea", "value": "output"}), [])

    def test_contract_hint_names_requested_elements_without_inventing_types(self):
        hint = contract_hint({"value": "output", "go": "button", "custom": None})
        self.assertIn("<output id=\"value\">", hint)
        self.assertIn("<button id=\"go\">", hint)
        self.assertIn("id=\"custom\" on any element", hint)
        self.assertEqual(contract_hint({}), "")

    def test_hint_is_bounded_but_validator_still_checks_all_ids(self):
        requirements = {"item" + str(n): None for n in range(100)}
        self.assertLess(len(contract_hint(requirements)), 8300)
        self.assertTrue(violations("<div id=item0></div>", requirements))


if __name__ == "__main__":
    unittest.main()
