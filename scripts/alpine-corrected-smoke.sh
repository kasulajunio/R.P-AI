#!/usr/bin/env bash
# Alpine only. This never targets an Android/Termux device.
set -euo pipefail
commit=${1:?Informe o SHA completo do commit a testar}
[[ $commit =~ ^[a-f0-9]{40}$ ]] || { echo SHA invalido >&2; exit 2; }
command -v apk >/dev/null || { echo Este teste exige Alpine >&2; exit 2; }
apk add --no-cache python3 py3-pip git github-cli unzip bash
: "${GH_TOKEN:?Autenticacao do GitHub necessaria para este repositorio privado}"
gh auth status >/dev/null 2>&1
pasta=$(mktemp -d "${TMPDIR:-/tmp}/rpa-corrected.XXXXXX")
# No token, notes or raw arguments are printed. Original script is retained separately.
gh api "repos/kasulajunio/R.P-AI/zipball/$commit" > "$pasta/projeto.zip"
[ -s "$pasta/projeto.zip" ] || { echo ZIP vazio >&2; exit 1; }
unzip -q "$pasta/projeto.zip" -d "$pasta"
src=( "$pasta"/kasulajunio-R.P-AI-* )
[ ${#src[@]} -eq 1 ] && [ -d "${src[0]}" ] || { echo Extracao inesperada >&2; exit 1; }
cd "${src[0]}"
python3 -m venv .venv
.venv/bin/python -m pip install .
.venv/bin/python -c "import platform, sysconfig; from official_core.forge import platform_key; print(dict(libc=platform.libc_ver(), target=sysconfig.get_config_var(\"HOST_GNU_TYPE\"), detected=platform_key()))"
.venv/bin/python rpa.py install
.venv/bin/python rpa.py status
.venv/bin/python rpa.py forge plan rg fd
.venv/bin/python -m compileall -q official_core tests
.venv/bin/python -m unittest discover -s tests -v
echo "ALPINE_CORRECTED_PASS commit=$commit; nenhum dispositivo Android foi acessado"
