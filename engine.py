"""Entrada compativel com o esqueleto original de Fabio."""
import sys
from official_core.engine import MasterEngine
from official_core.cli import main, menu

if __name__ == "__main__":
    raise SystemExit(main() if len(sys.argv) > 1 else menu())
