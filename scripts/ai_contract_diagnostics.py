# SPDX-License-Identifier: MIT
"""Run unchanged synthetic variants with structural metadata, never raw replies."""
import json
from pathlib import Path
import sys
import time
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from official_core import local_ai
from official_core.app_contract import HTML_PATTERN, Identifiers, requested_ids, violations
from scripts.ai_variants import main


def run():
    records = []
    original = local_ai.chat

    def traced_chat(messages, model=local_ai.DEFAULT_MODEL, **kwargs):
        answer = original(messages, model, **kwargs)
        prompt = messages[1]["content"].split("\n\nThe previous generation violated", 1)[0]
        required = requested_ids(prompt)
        match = HTML_PATTERN.search(answer)
        record = {"required": required, "complete_document_found": bool(match)}
        if match:
            document = match.group(0)
            parser = Identifiers()
            parser.feed(document)
            parser.close()
            record["found"] = dict(parser.elements)
            record["violations"] = violations(document, required)
        records.append(record)
        return answer

    try:
        with patch.object(local_ai, "chat", side_effect=traced_chat):
            return main()
    finally:
        path = Path("ai-contract-diagnostics-" + str(time.time_ns()) + ".json")
        path.write_text(json.dumps({"synthetic_cases_only": True, "raw_replies_saved": False, "calls": records}, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    run()
