# SPDX-License-Identifier: MIT
"""Independent real model requests, unchanged outputs tested in sandboxed browser."""
import html
import json
from pathlib import Path
import secrets
import shutil
import sys
import tempfile
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from official_core.assistant_cli import create_app
from official_core.local_ai import DEFAULT_MODEL
from scripts.ai_smoke import Preview, insert_script, run_browser

CASES = [
    ("step-counter",
     "Create a tiny complete HTML page, at most 50 lines, with html head body. A counter starts at 0 in output id=value. Buttons id=plus adds TWO, id=minus subtracts TWO, id=reset sets zero. Use textContent to update output. Exact ids value plus minus reset. Inline JS after buttons. No network, libraries or storage. End with </html>.",
     "const v=document.getElementById(\"value\");if(!v||Number(v.textContent)!==0)throw Error(\"initial\");document.getElementById(\"plus\").click();if(Number(v.textContent)!==2)throw Error(\"plus two\");document.getElementById(\"minus\").click();if(Number(v.textContent)!==0)throw Error(\"minus two\");document.getElementById(\"minus\").click();if(Number(v.textContent)!==-2)throw Error(\"negative\");document.getElementById(\"reset\").click();if(Number(v.textContent)!==0)throw Error(\"reset\");"),
    ("addition",
     "Create a tiny complete HTML page with html head body, at most 50 lines. Two numeric inputs id=a and id=b accept decimals and negatives. Button id=calculate displays their numeric SUM in output id=result with textContent. Use Number(input.value), not string concatenation. Exact ids a b calculate result. No other text inside output. Inline JS after controls. No network libraries storage. End with </html>.",
     "const a=document.getElementById(\"a\"),b=document.getElementById(\"b\"),r=document.getElementById(\"result\"),go=document.getElementById(\"calculate\");if(!a||!b||!r||!go)throw Error(\"controls\");for(const [x,y,z] of [[7,5,12],[1.5,2.25,3.75],[-5,2,-3],[0,0,0]]){a.value=String(x);b.value=String(y);go.click();if(Number(r.textContent.trim())!==z)throw Error(\"sum \"+x+\",\"+y+\" got \"+r.textContent);}"),
    ("temperature",
     "Create a tiny complete HTML page with html head body, at most 50 lines. Numeric input id=celsius, button id=convert, output id=result. Click converts Celsius to Fahrenheit with F=C*9/5+32. Result output contains ONLY the numeric value, no units or labels inside output. Support negatives and decimal input. Exact ids celsius convert result. Inline JS after controls, no network libraries storage. End with </html>.",
     "const c=document.getElementById(\"celsius\"),r=document.getElementById(\"result\"),go=document.getElementById(\"convert\");if(!c||!r||!go)throw Error(\"controls\");for(const [x,y] of [[0,32],[100,212],[-40,-40],[37,98.6]]){c.value=String(x);go.click();if(Math.abs(Number(r.textContent.trim())-y)>0.00001)throw Error(\"conversion \"+x+\" got \"+r.textContent);}"),
    ("text-meter",
     "Create a tiny complete HTML page with html head body, at most 50 lines. Textarea id=text, button id=count, output id=result. Clicking count displays text.value.length as a plain number using textContent. Empty text counts zero. Exact ids text count result. Treat all user input as text, never HTML. Inline JS after controls, no network libraries storage. End with </html>.",
     "const t=document.getElementById(\"text\"),r=document.getElementById(\"result\"),go=document.getElementById(\"count\");if(!t||!r||!go)throw Error(\"controls\");for(const s of [\"\",\"abc\",\"ola mundo\",\"<img src=x onerror=alert(1)>\"]){t.value=s;go.click();if(Number(r.textContent.trim())!==s.length)throw Error(\"length got \"+r.textContent);if(r.querySelector(\"img\"))throw Error(\"HTML injection\");}")
]


def main():
    chrome = shutil.which("google-chrome") or shutil.which("chromium")
    assert chrome, "Chrome required"
    evidence = {"model": DEFAULT_MODEL, "android_device_tested": False, "generated_outputs_repaired": False, "requests": []}
    artifacts = Path("ai-variant-artifacts")
    artifacts.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="rpa-ai-variants-") as folder:
        base = Path(folder).resolve()
        for name, prompt, checks in CASES:
            result = {"name": name, "prompt": prompt, "passed": False}
            started = time.monotonic()
            try:
                generated = create_app(base / "workspace", name, prompt=prompt, timeout=300)
                assert generated["source"] == "local_model_unreviewed"
                page = Path(generated["path"])
                wrapper = page.read_text(encoding="utf-8")
                (artifacts / (name + "-unreviewed.html")).write_text(wrapper, encoding="utf-8")
                preview = Preview()
                preview.feed(wrapper)
                assert preview.source, "Missing sandboxed preview"
                token = secrets.token_hex(16)
                child_test = "let result;try{" + checks + "result=\"passed\"}catch(e){result=\"failed:\"+e.message}parent.postMessage({rpaToken:" + json.dumps(token) + ",result},\"*\");"
                source = insert_script(preview.source, child_test)
                wrapper = wrapper.replace(html.escape(preview.source, quote=True), html.escape(source, quote=True), 1)
                parent_test = "window.addEventListener(\"message\",e=>{if(e.source===document.querySelector(\"iframe\").contentWindow&&e.data&&e.data.rpaToken===" + json.dumps(token) + "){document.body.dataset.rpaGeneratedTest=e.data.result}});"
                wrapper = wrapper.replace("<iframe ", "<script>" + parent_test + "</script><iframe ", 1)
                page.write_text(wrapper, encoding="utf-8")
                dom = run_browser(chrome, page, base / ("chrome-" + name))
                (artifacts / (name + "-browser.txt")).write_text(dom, encoding="utf-8")
                assert "data-rpa-generated-test=\"passed\"" in dom, "Generated behavior failed; inspect browser evidence"
                result["passed"] = True
                result["sandbox_preserved"] = True
            except Exception as error:
                result["error"] = {"type": type(error).__name__, "message": str(error)[:1000]}
            result["elapsed_seconds"] = round(time.monotonic() - started, 3)
            evidence["requests"].append(result)
            Path("ai-variants-evidence.json").write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8")
            print(json.dumps(result), flush=True)
    evidence["passed_count"] = sum(r["passed"] for r in evidence["requests"])
    evidence["total_count"] = len(CASES)
    evidence["passed"] = evidence["passed_count"] == len(CASES)
    Path("ai-variants-evidence.json").write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(evidence, indent=2), flush=True)
    return 0 if evidence["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
