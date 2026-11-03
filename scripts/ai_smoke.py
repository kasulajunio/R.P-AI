# SPDX-License-Identifier: MIT
"""Verificacao explicita em CI. Requer Ollama ja servido e modelo ja baixado."""
import json
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from official_core.local_ai import chat, DEFAULT_MODEL
from official_core.assistant_cli import create_app


def main():
    reply = chat([{"role": "user", "content": "Responda apenas OLA."}], timeout=300)
    assert reply.strip(), "Modelo sem resposta"
    with tempfile.TemporaryDirectory() as folder:
        root = Path(folder).resolve() / "workspace"
        generated = create_app(root, "generated", prompt="Crie um contador HTML minimo. Exiba um numero zero e um botao que aumenta o numero ao toque. Sem bibliotecas.", timeout=300)
        assert generated["source"] == "local_model_unreviewed"
        assert Path(generated["path"]).is_file()
        counter = create_app(root, "counter")
        page = Path(counter["path"])
        browser_test = """<script>try{const v=document.getElementById("value");document.getElementById("plus").click();if(v.textContent!=="1")throw Error("plus");document.getElementById("minus").click();if(v.textContent!=="0")throw Error("minus");document.getElementById("plus").click();document.getElementById("reset").click();if(v.textContent!=="0")throw Error("reset");document.body.dataset.rpaTest="passed"}catch(e){document.body.dataset.rpaTest="failed"}</script>"""
        page.write_text(page.read_text(encoding="utf-8").replace("</body>", browser_test + "</body>"), encoding="utf-8")
        chrome = shutil.which("google-chrome") or shutil.which("chromium")
        assert chrome, "Chrome/Chromium ausente: nao declarar teste do browser"
        result = subprocess.run([chrome, "--headless", "--no-sandbox", "--disable-gpu", "--no-first-run", "--user-data-dir=" + str(Path(folder) / "chrome"), "--dump-dom", page.as_uri()], capture_output=True, text=True, timeout=60, check=True, shell=False)
        assert "data-rpa-test=\"passed\"" in result.stdout, "Contador nao passou em navegador real"
    evidence = {"system": platform.system(), "architecture": platform.machine(), "model": DEFAULT_MODEL, "genuine_model_reply_received": True, "ai_html_generated": True, "counter_browser_interaction_passed": True, "generated_ai_app_behavior_tested": False, "android_device_tested": False}
    Path("ai-evidence.json").write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(evidence, indent=2))


if __name__ == "__main__":
    main()
