"""R.P AI, MIT, Copyright 2026 Fabio. Consulte LICENSE e TERMS.md.
Uso livre sob MIT; sem garantia nos limites da lei. Nao ha aceite juridico
automatico, instalacao de pacotes do sistema ou download de modelos.
"""
import sys
from official_core.launcher import main

if __name__ == "__main__":
    raise SystemExit(main([*sys.argv[1:], "install"]))
