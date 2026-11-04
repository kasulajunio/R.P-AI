# SPDX-License-Identifier: MIT
"""Regression for the real step-counter failure: wrong id silently saved."""
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from official_core import local_ai
from official_core.app_contract import requested_ids, violations
from official_core.assistant_cli import create_app

PROMPT = "A counter starts at 0 in output id=value. Buttons id=plus adds TWO, id=minus subtracts TWO, id=reset sets zero."
BAD = "<html><head></head><body><p id=counter>0</p><button id=plus>+</button><button id=minus>-</button><button id=reset>Reset</button></body></html>"
GOOD = BAD.replace("<p id=counter>0</p>", "<output id=value>0</output>")


class AppContractTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "workspace"

    def test_original_counter_id_failure_is_detected(self):
        requirements = requested_ids(PROMPT)
        self.assertEqual(set(requirements), {"value", "plus", "minus", "reset"})
        self.assertEqual(requirements["value"], "output")
        self.assertTrue(violations(BAD, requirements))
        self.assertEqual(violations(GOOD, requirements), [])

    def test_regeneration_preserves_request_and_sandbox(self):
        with patch.object(local_ai, "chat", side_effect=[BAD, GOOD]) as chat:
            result = create_app(self.root, "fixed", prompt=PROMPT)
        self.assertEqual(chat.call_count, 2)
        self.assertEqual(result["generation_attempts"], 2)
        first = chat.call_args_list[0].args[0][1]["content"]
        second = chat.call_args_list[1].args[0][1]["content"]
        self.assertEqual(first, PROMPT)
        self.assertTrue(second.startswith(PROMPT))
        self.assertIn("id=value", second)
        self.assertLessEqual(chat.call_args_list[1].kwargs["timeout"], 180)
        text = Path(result["path"]).read_text(encoding="utf-8")
        self.assertIn("sandbox=\"allow-scripts\"", text)
        self.assertNotIn("allow-same-origin", text)
        self.assertIn("&lt;output id=value&gt;", text)
        self.assertFalse(result["executed"])
        self.assertFalse(result["functional_tested"])

    def test_two_invalid_results_fail_without_saving(self):
        with patch.object(local_ai, "chat", return_value=BAD) as chat:
            with self.assertRaisesRegex(local_ai.LocalAIError, "apos 2 tentativas"):
                create_app(self.root, "rejected", prompt=PROMPT)
        self.assertEqual(chat.call_count, 2)
        self.assertFalse(self.root.exists())

    def test_valid_result_needs_one_call_templates_need_none(self):
        with patch.object(local_ai, "chat", return_value=GOOD) as chat:
            result = create_app(self.root, "valid", prompt=PROMPT)
        self.assertEqual(chat.call_count, 1)
        self.assertEqual(result["generation_attempts"], 1)
        with patch.object(local_ai, "chat", side_effect=AssertionError("No model")):
            result = create_app(self.root, "offline")
        self.assertEqual(result["generation_attempts"], 0)

    def test_duplicate_wrong_type_and_inert_template_rejected(self):
        contract = {"value": "output"}
        for document in ["<p id=value>0</p>", "<output id=value>0</output><output id=value>1</output>", "<template><output id=value>0</output></template>"]:
            with self.subTest(document=document):
                self.assertTrue(violations(document, contract))

    def test_comments_and_script_strings_do_not_satisfy_ids(self):
        contract = {"value": "output"}
        for document in ["<!-- <output id=value>0</output> -->", "<script>const s=\"<output id=value>0</output>\";</script>"]:
            self.assertTrue(violations(document, contract))

    def test_quoted_ids_and_case_sensitive_values(self):
        prompt = "<output id=\"Value\">0</output> and button id=go"
        self.assertEqual(requested_ids(prompt), {"Value": "output", "go": "button"})
        self.assertTrue(violations("<output id=value></output><button id=go></button>", requested_ids(prompt)))
        self.assertEqual(violations("<OUTPUT ID=Value></OUTPUT><BUTTON ID=go></BUTTON>", requested_ids(prompt)), [])
        self.assertEqual(requested_ids("output id=" + chr(39) + "value" + chr(39)), {"value": "output"})

    def test_retry_does_not_reset_timeout_budget(self):
        with patch("official_core.app_contract.time.monotonic", side_effect=[100, 102]), patch.object(local_ai, "chat", return_value=BAD) as chat:
            with self.assertRaisesRegex(local_ai.LocalAIError, "Tempo de geracao"):
                create_app(self.root, "expired", prompt=PROMPT, timeout=2)
        self.assertEqual(chat.call_count, 1)
        self.assertFalse(self.root.exists())

    def test_model_error_does_not_trigger_blind_retry(self):
        with patch.object(local_ai, "chat", side_effect=local_ai.LocalAIError("offline")) as chat:
            with self.assertRaisesRegex(local_ai.LocalAIError, "offline"):
                create_app(self.root, "offline-error", prompt=PROMPT)
        self.assertEqual(chat.call_count, 1)
        self.assertFalse(self.root.exists())


if __name__ == "__main__":
    unittest.main()
