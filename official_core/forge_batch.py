# SPDX-License-Identifier: MIT
"""Explicit batch wrapper; delegates all downloads to the approved Forge."""
import argparse
import json
import sys
from .forge import Forge


def execute_batch(tools, *, install=False, allow_network=False, directory=None):
    if not isinstance(tools, (list, tuple)) or not tools or len(tools) > 32:
        raise ValueError("Informe de 1 a 32 ferramentas aprovadas")
    if any(not isinstance(tool, str) for tool in tools):
        raise ValueError("Nomes devem ser texto")
    if len(set(tools)) != len(tools):
        raise ValueError("Ferramentas duplicadas no lote")
    if install and not allow_network:
        raise PermissionError("install exige --allow-network")
    forge = Forge(directory)
    # Resolve every item offline before the first possible download.
    plans = [{"tool": tool, **forge.ensure(tool, install=False)} for tool in tools]
    if not install:
        return {"status": "planned", "mode": "plan", "items": plans}
    completed = []
    for index, plan in enumerate(plans):
        tool = tools[index]
        try:
            result = forge.ensure(tool, install=True)
        except (OSError, ValueError, RuntimeError) as error:
            return {"status": "partial" if completed else "failed", "mode": "install",
                    "items": completed, "failed_tool": tool,
                    "error_type": type(error).__name__, "not_attempted": list(tools[index + 1:])}
        completed.append({"tool": tool, **result})
    return {"status": "complete", "mode": "install", "items": completed}


def main(argv=None):
    parser = argparse.ArgumentParser(description="Forge batch: pre-validacao offline e instalacao explicita")
    parser.add_argument("action", choices=["plan", "install"])
    parser.add_argument("tools", nargs="+")
    parser.add_argument("--directory")
    parser.add_argument("--allow-network", action="store_true")
    args = parser.parse_args(argv)
    if args.action == "install" and not args.allow_network:
        parser.error("install exige --allow-network")
    try:
        report = execute_batch(args.tools, install=args.action == "install",
                               allow_network=args.allow_network, directory=args.directory)
    except (OSError, ValueError, RuntimeError) as error:
        print("Batch bloqueado: " + type(error).__name__ + ". Nenhum download de lote iniciado.", file=sys.stderr)
        return 1
    print(json.dumps(report, indent=2))
    return 0 if report["status"] in ("planned", "complete") else 1


if __name__ == "__main__":
    raise SystemExit(main())
