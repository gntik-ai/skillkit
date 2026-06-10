#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = []  # p.ej. ["requests>=2"]
# ///
"""{{NAME}} — {{DESCRIPTION}}

Categoría: {{CATEGORY}} · Herramienta base: {{BASE}}

Convenciones del repo:
  - datos por stdout; mensajes/errores por stderr
  - --json para salida estructurada; --help funciona sin dependencias
  - dependencias en línea (PEP 723), ejecutar con `uv run`
  - el import de dependencias va DENTRO de main(): --help no las necesita
  - exit: 0 ok · 1 ejecución · 2 uso (argparse) · 3 sin resultado · 127 falta dependencia
"""
from __future__ import annotations

import argparse
import json
import sys


def eprint(*args: object) -> None:
    print(*args, file=sys.stderr)


def main() -> int:
    parser = argparse.ArgumentParser(prog="{{NAME}}", description="{{DESCRIPTION}}")
    parser.add_argument("--json", action="store_true", help="Salida JSON")
    args = parser.parse_args()

    # Import perezoso de dependencias: --help funciona sin instalarlas.
    # try:
    #     import requests
    # except ImportError:
    #     eprint("[{{NAME}}] error: faltan dependencias; ejecuta el script con `uv run`")
    #     return 127

    eprint("[{{NAME}}] TODO: implementar")
    if args.json:
        print(json.dumps({"todo": True}, ensure_ascii=False))
    return 1


if __name__ == "__main__":
    sys.exit(main())
