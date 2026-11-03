"""R.P AI, MIT, Copyright 2026 Fabio. Consulte LICENSE e TERMS.md.
Uso livre sob MIT; sem garantia nos limites da lei. Nao ha aceite juridico
automatico, instalacao de pacotes do sistema ou download de modelos.
"""
import argparse
from official_core.launcher import main

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Boot local offline da R.P AI")
    parser.add_argument("--root", default=".core")
    parser.add_argument("--no-venv", action="store_true")
    args = parser.parse_args()
    raise SystemExit(main(["--root", args.root, "install"] + (["--no-venv"] if args.no_venv else [])))
