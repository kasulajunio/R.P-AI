#!/usr/bin/env bash
set -euo pipefail
apk update
apk add --no-cache python3 py3-pip py3-venv git github-cli zip unzip curl bash
gh auth status
pasta=$(mktemp -d "$HOME/rpa-teste.XXXXXX")
echo "Baixando em $pasta ..."
gh api repos/kasulajunio/R.P-AI/zipball/8c378b7691979ca151c5a5aea0ed7ae010ba57ff > "$pasta/projeto.zip"
[ -s "$pasta/projeto.zip" ] || { echo "zip vazio, abortando"; exit 1; }
unzip -q "$pasta/projeto.zip" -d "$pasta"
src=( "$pasta"/kasulajunio-R.P-AI-* )
[ ${#src[@]} -eq 1 ] && [ -d "${src[0]}" ] || { echo "extração inesperada"; exit 1; }
cd "${src[0]}"
ls -la
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
if [ -f requirements.txt ]; then
 pip install -r requirements.txt
else
 echo "AVISO: requirements.txt não encontrado"
fi
echo "venv pronto"
python rpa.py install
python rpa.py status
python rpa.py forge plan rg fd
