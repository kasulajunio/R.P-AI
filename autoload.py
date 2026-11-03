"""Startup opcional, MIT. Nenhum registro de servico e feito por este arquivo."""
import argparse
from official_core.launcher import main as rpa


def main(argv=None):
    parser = argparse.ArgumentParser(description="R.P AI startup local, sem loop em segundo plano")
    parser.add_argument("--root", default=".core")
    parser.add_argument("--source")
    parser.add_argument("--auto-update", action="store_true")
    parser.add_argument("--no-venv", action="store_true")
    args = parser.parse_args(argv)
    common = ["--root", args.root]
    if args.source:
        common += ["--source", args.source]
    if args.auto_update:
        code = rpa(common + ["update"])
        if code:
            return code
    code = rpa(common + ["install"] + (["--no-venv"] if args.no_venv else []))
    if code:
        return code
    return rpa(common + ["run", "db-check"])


if __name__ == "__main__":
    raise SystemExit(main())
