# SPDX-License-Identifier: MIT
"""Unified, explicitly authorized Forge CLI batches; no arbitrary URLs."""
import argparse
import json
import sys
import tarfile
import zipfile
from . import forge_archives
from .forge import CATALOG, Forge


def execute(tools, *, directory=None, install=False, allow_network=False):
    if (not isinstance(tools, (list, tuple)) or not tools or len(tools) > 32
            or any(not isinstance(t, str) for t in tools) or len(set(tools)) != len(tools)):
        raise ValueError("Informe ferramentas aprovadas, sem duplicatas")
    if install and not allow_network:
        raise PermissionError("install exige --allow-network")
    approved = set(CATALOG) | set(forge_archives.CATALOG)
    if any(tool not in approved for tool in tools):
        raise ValueError("Ferramenta fora do catalogo aprovado")
    forge = Forge(directory)
    plans = []
    for tool in tools:
        if tool in forge_archives.CATALOG:
            plans.append(forge_archives.plan(tool, directory))
        else:
            plans.append({"tool": tool, **forge.ensure(tool, install=False)})
    if not install:
        return {"status": "planned", "mode": "plan", "items": plans}
    completed = []
    for index, item in enumerate(plans):
        try:
            if item["tool"] in forge_archives.CATALOG:
                result = forge_archives.install_planned(item)
            else:
                result = {"tool": item["tool"], **forge.ensure(item["tool"], install=True)}
            completed.append(result)
        except (OSError, ValueError, RuntimeError, tarfile.TarError, zipfile.BadZipFile, EOFError) as error:
            return {"status": "partial" if completed else "failed", "mode": "install",
                    "items": completed, "failed_tool": item["tool"],
                    "error_type": type(error).__name__, "not_attempted": list(tools[index + 1:])}
    return {"status": "complete", "mode": "install", "items": completed}


def main(argv=None):
    parser = argparse.ArgumentParser(description="Forge integrado: jq, rg e fd do catalogo fixo")
    parser.add_argument("action", choices=["plan", "install"])
    parser.add_argument("tools", nargs="+")
    parser.add_argument("--directory")
    parser.add_argument("--allow-network", action="store_true")
    args = parser.parse_args(argv)
    if args.action == "install" and not args.allow_network:
        parser.error("install exige --allow-network")
    try:
        report = execute(args.tools, directory=args.directory, install=args.action == "install", allow_network=args.allow_network)
    except (OSError, ValueError, RuntimeError) as error:
        print("Forge bloqueado: " + type(error).__name__ + ". Nenhum download iniciado.", file=sys.stderr)
        return 1
    print(json.dumps(report, indent=2))
    return 0 if report["status"] in ("planned", "complete") else 1


if __name__ == "__main__":
    raise SystemExit(main())
