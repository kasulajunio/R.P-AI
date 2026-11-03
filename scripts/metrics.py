import ast
import json
import unittest
from pathlib import Path

files = sorted(Path("official_core").glob("*.py")) + [Path("engine.py")]
metrics = {"python_files": len(files), "source_lines": 0, "functions": 0}
for path in files:
    text = path.read_text(encoding="utf-8")
    metrics["source_lines"] += len(text.splitlines())
    metrics["functions"] += sum(isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) for node in ast.walk(ast.parse(text)))
metrics["test_cases"] = unittest.defaultTestLoader.discover("tests").countTestCases()
print("::notice title=Core metrics::" + json.dumps(metrics, sort_keys=True))
