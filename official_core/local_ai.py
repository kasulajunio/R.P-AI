# SPDX-License-Identifier: MIT
"""Ollama local opt-in. Nao baixa modelos nem executa comandos."""
import json
import math
from urllib.error import HTTPError, URLError
from urllib.request import HTTPRedirectHandler, ProxyHandler, Request, build_opener

ENDPOINT = "http://127.0.0.1:11434/api/chat"
DEFAULT_MODEL = "qwen2.5-coder:0.5b"
MODELS = (DEFAULT_MODEL, "qwen2.5-coder:1.5b", "qwen2.5-coder:3b")
MAX_BYTES = 128 * 1024


class LocalAIError(RuntimeError):
    pass


class _NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise LocalAIError("Redirecionamento recusado: o modelo deve permanecer local")


def chat(messages, model=DEFAULT_MODEL, *, timeout=180):
    if model not in MODELS:
        raise LocalAIError("Escolha um modelo local documentado; modelos cloud nao sao aceitos")
    if not isinstance(timeout, (int, float)) or not math.isfinite(timeout) or not 1 <= timeout <= 600:
        raise LocalAIError("Timeout deve estar entre 1 e 600 segundos")
    if not isinstance(messages, list) or not 1 <= len(messages) <= 32:
        raise LocalAIError("Historico deve conter entre 1 e 32 mensagens")
    clean = []
    for message in messages:
        if not isinstance(message, dict) or message.get("role") not in {"system", "user", "assistant"}:
            raise LocalAIError("Papel de mensagem invalido")
        content = message.get("content")
        if not isinstance(content, str) or not content.strip() or len(content) > 16000:
            raise LocalAIError("Mensagem vazia ou acima de 16000 caracteres")
        clean.append({"role": message["role"], "content": content})
    body = json.dumps({"model": model, "messages": clean, "stream": False, "options": {"num_ctx": 4096, "num_predict": 1536, "temperature": 0.2}}, ensure_ascii=False).encode("utf-8")
    if len(body) > MAX_BYTES:
        raise LocalAIError("Historico excede o limite de envio")
    request = Request(ENDPOINT, data=body, headers={"Content-Type": "application/json", "Accept": "application/json"}, method="POST")
    opener = build_opener(ProxyHandler({}), _NoRedirect())
    try:
        with opener.open(request, timeout=timeout) as response:
            raw = response.read(MAX_BYTES + 1)
        if len(raw) > MAX_BYTES:
            raise LocalAIError("Resposta do modelo excede o limite")
        result = json.loads(raw.decode("utf-8"))
    except HTTPError as error:
        code = error.code
        error.close()
        if code == 404:
            raise LocalAIError("Modelo nao encontrado. Baixe-o explicitamente com ollama pull") from None
        raise LocalAIError("O servidor local recusou a solicitacao (HTTP " + str(code) + ")") from None
    except (URLError, OSError):
        raise LocalAIError("Ollama indisponivel ou demorou demais. Inicie ollama serve em outra sessao do Termux") from None
    except (UnicodeError, ValueError):
        raise LocalAIError("O servidor local devolveu uma resposta invalida") from None
    if not isinstance(result, dict) or result.get("done") is not True:
        raise LocalAIError("Resposta incompleta; nenhum resultado foi tratado como concluido")
    message = result.get("message")
    if not isinstance(message, dict) or message.get("role") != "assistant":
        raise LocalAIError("Mensagem de resposta invalida")
    text = message.get("content")
    if not isinstance(text, str) or not text.strip():
        raise LocalAIError("O modelo nao produziu texto")
    return text.strip()
