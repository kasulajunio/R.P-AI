# SPDX-License-Identifier: MIT
"""Validate explicit HTML identifiers without executing generated code."""
from collections import defaultdict
from html.parser import HTMLParser
import re
import time
from . import local_ai

SYSTEM = ("Crie apenas um documento HTML completo pequeno, com html, head e body. "
          "Use CSS e JavaScript inline, sem rede, armazenamento, formularios, permissoes ou dependencias. "
          "Deve funcionar pelo toque no celular. Termine com </html>. "
          "Respect every exact HTML id and element type explicitly requested. Never rename requested ids.")
ID_PATTERN = re.compile(r"\bid\s*=\s*(?:\"([^\"\s<>]+)\"|\x27([^\x27\s<>]+)\x27|([A-Za-z_][A-Za-z0-9_:.-]*))", re.I)
TAG_PATTERN = re.compile(r"\b(output|button|input|textarea|select|canvas)s?\s*$", re.I)
HTML_PATTERN = re.compile(r"(?:<!doctype\s+html[^>]*>\s*)?<html(?:\s[^>]*)?>.*?</html\s*>", re.I | re.S)


def requested_ids(prompt):
    result = {}
    for match in ID_PATTERN.finditer(prompt):
        identifier = next(value for value in match.groups() if value is not None)
        prefix = prompt[:match.start()]
        # In prose, the final full stop terminates the sentence, not the ID.
        # Quoted values and attributes inside explicit HTML remain literal.
        inside_html = prefix.rfind("<") > prefix.rfind(">")
        if match.group(3) is not None and not inside_html:
            identifier = identifier.rstrip(".")
        tag = TAG_PATTERN.search(prefix)
        if identifier not in result or tag:
            result[identifier] = tag.group(1).lower() if tag else None
    return result


class Identifiers(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.elements = defaultdict(list)
        self.template_depth = 0

    def handle_starttag(self, tag, attrs):
        if tag == "template":
            self.template_depth += 1
        if self.template_depth:
            return
        for key, value in attrs:
            if key == "id" and value is not None:
                self.elements[value].append(tag)

    def handle_endtag(self, tag):
        if tag == "template" and self.template_depth:
            self.template_depth -= 1


def violations(document, requirements):
    parser = Identifiers()
    try:
        parser.feed(document)
        parser.close()
    except (AssertionError, ValueError):
        raise local_ai.LocalAIError("HTML invalido; nenhum app foi salvo") from None
    errors = []
    for identifier, tag in requirements.items():
        found = parser.elements.get(identifier, [])
        if len(found) != 1:
            errors.append("id=" + identifier + " must occur exactly once")
        elif tag and found[0] != tag:
            errors.append("id=" + identifier + " must use <" + tag + ">")
    return errors


def generate_document(prompt, *, model=local_ai.DEFAULT_MODEL, timeout=180):
    requirements = requested_ids(prompt)
    started = time.monotonic()
    correction = ""
    for attempt in range(2):
        remaining = timeout if attempt == 0 else timeout - (time.monotonic() - started)
        if attempt and remaining < 1:
            raise local_ai.LocalAIError("Tempo de geracao esgotado; nenhum app foi salvo")
        messages = [{"role": "system", "content": SYSTEM},
                    {"role": "user", "content": prompt + correction}]
        answer = local_ai.chat(messages, model, timeout=remaining)
        match = HTML_PATTERN.search(answer)
        if not match:
            raise local_ai.LocalAIError("O modelo nao entregou HTML completo. Tente um pedido menor; nenhum app foi salvo")
        document = match.group(0)
        errors = violations(document, requirements) if requirements else []
        if not errors:
            return document, attempt + 1
        correction = ("\n\nThe previous generation violated these explicit requirements: "
                      + "; ".join(error[:180] for error in errors[:20])
                      + ". Generate a NEW complete HTML document. Preserve every requested id and the original behavior.")
    raise local_ai.LocalAIError("O modelo nao respeitou os IDs HTML exigidos apos 2 tentativas; nenhum app foi salvo")
