# SPDX-License-Identifier: MIT
"""Chat opt-in e miniapps HTML. Sem execucao automatica de codigo."""
import html
import json
import re
import sys
import unicodedata
from . import local_ai
from .app_contract import generate_document
from .engine import MasterEngine

SYSTEM = "Voce e R.P AI. Responda em portugues brasileiro. Seja claro e honesto. Nao afirme ter executado comandos ou controlado o celular: voce so produz texto."
Q = chr(39)
CSP = "default-src " + Q + "none" + Q + "; script-src " + Q + "unsafe-inline" + Q + "; style-src " + Q + "unsafe-inline" + Q + "; img-src data:; connect-src " + Q + "none" + Q + "; frame-src " + Q + "self" + Q + "; base-uri " + Q + "none" + Q + "; form-action " + Q + "none" + Q
STYLE = "body{margin:0;background:#101820;color:#eef2f6;font:17px system-ui;padding:24px}main{max-width:640px;margin:auto}button,input{font:inherit;padding:14px;border-radius:12px;margin:6px;border:1px solid #586577}button{background:#b5d5ef;color:#101820;cursor:pointer}input{max-width:90%}output{display:block;font-size:64px;margin:28px}li{margin:12px 0}iframe{width:100%;height:75vh;border:0;background:white;border-radius:12px}"


def add_parsers(commands):
    chat = commands.add_parser("chat", help="Conversa com Ollama local; sem download automatico")
    chat.add_argument("message", nargs="?", help="Sem mensagem abre conversa; /sair encerra")
    chat.add_argument("--model", choices=local_ai.MODELS, default=local_ai.DEFAULT_MODEL)
    chat.add_argument("--timeout", type=float, default=180)
    app = commands.add_parser("app", help="Gera miniapp HTML local, nao APK")
    actions = app.add_subparsers(dest="app_action", required=True)
    create = actions.add_parser("create")
    create.add_argument("name", help="Letras minusculas, numeros e hifen")
    choice = create.add_mutually_exclusive_group()
    choice.add_argument("--template", choices=["counter", "todo"], default="counter")
    choice.add_argument("--prompt", help="Solicita HTML ao modelo local")
    create.add_argument("--model", choices=local_ai.MODELS, default=local_ai.DEFAULT_MODEL)
    create.add_argument("--timeout", type=float, default=180)


def _display(text):
    return "".join(c for c in text if c in "\n\t" or not unicodedata.category(c).startswith("C"))


def _page(title, body):
    return "<!doctype html><html lang=\"pt-BR\"><head><meta charset=\"utf-8\"><meta name=\"viewport\" content=\"width=device-width,initial-scale=1\"><meta http-equiv=\"Content-Security-Policy\" content=\"" + html.escape(CSP, quote=True) + "\"><title>" + html.escape(title) + "</title><style>" + STYLE + "</style></head><body><main>" + body + "</main></body></html>"


def _template(kind, name):
    heading = "<h1>" + html.escape(name) + "</h1>"
    if kind == "counter":
        return _page(name, heading + """<p>Meu primeiro miniapp R.P AI</p><output id="value" aria-live="polite">0</output><button id="minus" aria-label="Diminuir">-1</button><button id="plus" aria-label="Aumentar">+1</button><button id="reset">Zerar</button><script>let n=0;const value=document.getElementById("value");function draw(){value.textContent=String(n)}document.getElementById("plus").onclick=()=>{n++;draw()};document.getElementById("minus").onclick=()=>{n--;draw()};document.getElementById("reset").onclick=()=>{n=0;draw()};</script>""")
    if kind != "todo":
        raise ValueError("Template desconhecido")
    return _page(name, heading + """<p>Lista temporaria. Recarregar apaga os itens.</p><label for="task">Nova tarefa</label><input id="task" maxlength="200"><button id="add">Adicionar</button><ul id="list"></ul><script>const input=document.getElementById("task");document.getElementById("add").onclick=()=>{const text=input.value.trim();if(!text)return;const li=document.createElement("li");const label=document.createElement("span");label.textContent=text;const done=document.createElement("button");done.textContent="Concluir";done.onclick=()=>li.remove();li.append(label,done);document.getElementById("list").append(li);input.value="";input.focus()};</script>""")


def create_app(root, name, *, template="counter", prompt=None, model=local_ai.DEFAULT_MODEL, timeout=180):
    if not re.fullmatch(r"[a-z][a-z0-9-]{0,47}", name):
        raise ValueError("Nome limitado a 48 caracteres: letras minusculas, numeros e hifen")
    engine = MasterEngine(root)
    relative = "Miniapps/" + name + "/index.html"
    target = engine.path(relative)
    if target.exists():
        raise FileExistsError("Miniapp existente: escolha outro nome; nada foi sobrescrito")
    generation_attempts = 0
    if prompt is None:
        document = _template(template, name)
        source = "offline_template"
    else:
        if not prompt.strip() or len(prompt) > 8000:
            raise ValueError("Pedido deve ter entre 1 e 8000 caracteres")
        generated_html, generation_attempts = generate_document(prompt, model=model, timeout=timeout)
        embedded = html.escape(generated_html, quote=True)
        document = _page(name, "<h1>" + html.escape(name) + "</h1><p>Rascunho de IA. Revise antes de abrir. Nao forneca dados pessoais.</p><iframe title=\"Rascunho do miniapp\" sandbox=\"allow-scripts\" referrerpolicy=\"no-referrer\" srcdoc=\"" + embedded + "\"></iframe>")
        source = "local_model_unreviewed"
    if not engine._write_new(relative, document):
        raise FileExistsError("Destino criado por outra operacao; nada foi sobrescrito")
    return {"status": "html_created", "path": str(target), "source": source, "apk": False, "executed": False, "functional_tested": False, "generation_attempts": generation_attempts}


def run(args):
    try:
        if args.command == "app":
            result = create_app(args.root, args.name, template=args.template, prompt=args.prompt, model=args.model, timeout=args.timeout)
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0
        history = [{"role": "system", "content": SYSTEM}]
        if args.message is not None:
            history.append({"role": "user", "content": args.message})
            print(_display(local_ai.chat(history, args.model, timeout=args.timeout)))
            return 0
        print("R.P AI local. /sair encerra. Historico apenas na memoria desta sessao.")
        while True:
            try:
                prompt = input("Voce: ").strip()
            except (EOFError, KeyboardInterrupt):
                print()
                return 0
            if prompt.lower() in {"/sair", "/exit"}:
                return 0
            if not prompt:
                continue
            history.append({"role": "user", "content": prompt})
            answer = local_ai.chat(history, args.model, timeout=args.timeout)
            print("R.P AI: " + _display(answer))
            history.append({"role": "assistant", "content": answer})
            while len(history) > 3 and (len(history) > 13 or sum(len(m["content"]) for m in history) > 16000):
                del history[1:3]
    except (local_ai.LocalAIError, OSError, ValueError) as error:
        print("Falha: " + _display(str(error)), file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("Cancelado. Nenhum comando de modelo foi executado.", file=sys.stderr)
        return 130
