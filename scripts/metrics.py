import ast
import json
import sys
import unittest
from pathlib import Path

root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root))
files = sorted((root / "official_core").glob("*.py")) + [root / "engine.py"]
metrics = {"python_files": len(files), "source_lines": 0, "functions": 0}
for path in files:
    text = path.read_text(encoding="utf-8")
    metrics["source_lines"] += len(text.splitlines())
    metrics["functions"] += sum(isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) for node in ast.walk(ast.parse(text)))
loader = unittest.TestLoader()
suite = loader.discover(str(root / "tests"))
if loader.errors:
    raise RuntimeError("Test discovery failed: " + "; ".join(loader.errors))
metrics["test_cases"] = suite.countTestCases()
print("::notice title=Core metrics::" + json.dumps(metrics, sort_keys=True))
