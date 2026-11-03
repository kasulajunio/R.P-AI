# SPDX-License-Identifier: MIT
"""Explicit real CPU model and browser tests; no device claims."""
import html
from html.parser import HTMLParser
import json
from pathlib import Path
import platform
import secrets
import shutil
import subprocess
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from official_core.local_ai import chat, DEFAULT_MODEL
from official_core.assistant_cli import create_app


class Preview(HTMLParser):
    def __init__(self):
        super().__init__()
        self.source = None

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if tag == "iframe" and "srcdoc" in values:
            assert values.get("sandbox") == "allow-scripts"
            self.source = values["srcdoc"]


def insert_script(document, script):
    assert "</body>" in document.lower(), "HTML has no closing body"
    index = document.lower().rfind("</body>")
    return document[:index] + "<script>" + script + "</script>" + document[index:]


def run_browser(chrome, page, profile):
    result = subprocess.run([chrome, "--headless", "--no-sandbox", "--disable-gpu", "--no-first-run", "--disable-background-networking", "--host-resolver-rules=MAP * ~NOTFOUND", "--virtual-time-budget=5000", "--user-data-dir=" + str(profile), "--dump-dom", page.as_uri()], capture_output=True, text=True, timeout=60, check=True, shell=False)
    return result.stdout


COUNTER = "const v=document.getElementById(\"value\");if(!v||v.textContent.trim()!==\"0\")throw Error(\"initial value\");document.getElementById(\"plus\").click();if(v.textContent.trim()!==\"1\")throw Error(\"increment\");document.getElementById(\"minus\").click();if(v.textContent.trim()!==\"0\")throw Error(\"decrement\");document.getElementById(\"plus\").click();document.getElementById(\"reset\").click();if(v.textContent.trim()!==\"0\")throw Error(\"reset\");"
TODO = "const i=document.getElementById(\"task\"),a=document.getElementById(\"add\"),l=document.getElementById(\"list\");a.click();if(l.children.length!==0)throw Error(\"empty task\");i.value=\"<img src=x onerror=alert(1)>\";a.click();if(l.children.length!==1||l.querySelector(\"img\")||!l.textContent.includes(\"<img\"))throw Error(\"unsafe task\");l.querySelector(\"button\").click();if(l.children.length!==0)throw Error(\"complete task\");"


def main():
    reply = chat([{"role": "user", "content": "Responda apenas OLA."}], timeout=300)
    assert reply.strip(), "No actual model reply"
    chrome = shutil.which("google-chrome") or shutil.which("chromium")
    assert chrome, "A real Chrome or Chromium is required"
    with tempfile.TemporaryDirectory() as folder:
        base = Path(folder).resolve()
        root = base / "workspace"
        for template, checks in [("counter", COUNTER), ("todo", TODO)]:
            created = create_app(root, template, template=template)
            assert created["source"] == "offline_template"
            page = Path(created["path"])
            document = page.read_text(encoding="utf-8")
            test = "try{" + checks + "document.body.dataset.rpaTest=\"passed\"}catch(e){document.body.dataset.rpaTest=\"failed:\"+e.message}"
            page.write_text(insert_script(document, test), encoding="utf-8")
            dom = run_browser(chrome, page, base / ("chrome-" + template))
            assert "data-rpa-test=\"passed\"" in dom, template + " failed in real browser: " + dom[-3000:]
        prompt = "Create a tiny complete HTML document with html, head and body. Counter starts at 0 in <output id=\"value\">0</output>. Three buttons: id=\"plus\" increments by 1, id=\"minus\" decrements by 1, id=\"reset\" resets to 0. Inline JavaScript after buttons updates output.textContent. No network or libraries. Keep the exact ids value, plus, minus, reset. End with </html>."
        generated = create_app(root, "generated", prompt=prompt, timeout=300)
        assert generated["source"] == "local_model_unreviewed"
        page = Path(generated["path"])
        wrapper = page.read_text(encoding="utf-8")
        preview = Preview()
        preview.feed(wrapper)
        assert preview.source, "No sandboxed generated preview"
        token = secrets.token_hex(16)
        child_test = "let result;try{" + COUNTER + "result=\"passed\"}catch(e){result=\"failed:\"+e.message}parent.postMessage({rpaToken:" + json.dumps(token) + ",result},\"*\");"
        tested_source = insert_script(preview.source, child_test)
        wrapper = wrapper.replace(html.escape(preview.source, quote=True), html.escape(tested_source, quote=True), 1)
        parent_test = "window.addEventListener(\"message\",e=>{if(e.source===document.querySelector(\"iframe\").contentWindow&&e.data&&e.data.rpaToken===" + json.dumps(token) + "){document.body.dataset.rpaGeneratedTest=e.data.result}});"
        wrapper = wrapper.replace("<iframe ", "<script>" + parent_test + "</script><iframe ", 1)
        page.write_text(wrapper, encoding="utf-8")
        dom = run_browser(chrome, page, base / "chrome-generated")
        assert "data-rpa-generated-test=\"passed\"" in dom, "Generated counter failed in sandboxed iframe: " + dom[-4500:]
    evidence = {"system": platform.system(), "architecture": platform.machine(), "model": DEFAULT_MODEL, "genuine_model_reply_received": True, "ai_html_generated": True, "counter_browser_interaction_passed": True, "todo_browser_interaction_passed": True, "todo_html_injection_blocked": True, "generated_ai_app_behavior_tested": True, "generated_counter_increment_decrement_reset_passed": True, "generated_iframe_sandbox_preserved": True, "android_device_tested": False}
    Path("ai-evidence.json").write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(evidence, indent=2))


if __name__ == "__main__":
    main()
