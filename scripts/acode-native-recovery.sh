#!/bin/sh
# Disposable CI container only. Never targets the user device.
set -eu
apk add --no-cache python3
mkdir /work
cp -a /source/. /work/
cd /work
python3 -m venv .venv
.venv/bin/python - <<"PY"
import platform
from official_core.forge import platform_key
print(platform.machine(), platform_key())
assert platform_key() == "android-aarch64"
PY
.venv/bin/python rpa.py install
.venv/bin/python rpa.py status
if .venv/bin/python rpa.py forge plan rg fd; then
  echo Unexpected success before native packages >&2
  exit 1
fi
apk add --no-cache ripgrep fd
rg --version
fd --version
.venv/bin/python rpa.py forge plan rg fd > /tmp/plan.json
cat /tmp/plan.json
.venv/bin/python - <<"PY"
import json
with open("/tmp/plan.json") as stream:
    report = json.load(stream)
nodes = []
def walk(value):
    if isinstance(value, dict):
        nodes.append(value)
        for item in value.values():
            walk(item)
    elif isinstance(value, list):
        for item in value:
            walk(item)
walk(report)
tools = [item for item in nodes if item.get("tool") in ("rg", "fd")]
assert {item["tool"] for item in tools} == {"rg", "fd"}
assert all(item.get("status") == "system_available" and item.get("downloaded") is False for item in tools)
print("ACODE_NATIVE_RECOVERY_PASS")
PY
.venv/bin/python -m compileall -q official_core
