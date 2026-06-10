#!/usr/bin/env bash
#
# {{NAME}} — {{DESCRIPTION}}
# Categoría: {{CATEGORY}} · Herramienta base: {{BASE}}
#
# Convenciones del repo:
#   - datos por stdout; mensajes/errores por stderr
#   - --json para salida estructurada; --help funciona sin dependencias
#   - validar argumentos (exit 2) ANTES de comprobar dependencias (exit 127)
#   - exit: 0 ok · 1 error de ejecución · 2 uso incorrecto · 127 falta herramienta
#   - si el script escribe/borra: añadir --dry-run (sin requerir credenciales)

set -euo pipefail

usage() {
  cat <<'EOF'
{{NAME}} — {{DESCRIPTION}}

Uso:
  {{NAME}} [argumentos] [opciones]

Opciones:
      --json    Salida JSON
  -h, --help    Esta ayuda
EOF
}

# La ayuda funciona aunque falte la herramienta base.
for arg in "$@"; do case "$arg" in -h|--help) usage; exit 0 ;; esac; done

JSON=0
declare -a POSITIONAL=()
while [[ $# -gt 0 ]]; do
  case "$1" in
    --json)  JSON=1; shift ;;
    -*)      echo "[{{NAME}}] opción desconocida: $1" >&2; exit 2 ;;
    *)       POSITIONAL+=("$1"); shift ;;
  esac
done

# 1) Validación de uso (exit 2).
# [[ ${#POSITIONAL[@]} -ge 1 ]] || { echo "[{{NAME}}] falta un argumento" >&2; usage >&2; exit 2; }

# 2) Dependencia (exit 127).
command -v {{BASE}} >/dev/null 2>&1 || {
  echo "[{{NAME}}] error: '{{BASE}}' no está instalado" >&2
  exit 127
}

# 3) Lógica. Recuerda: datos → stdout; logs → stderr.
echo "[{{NAME}}] TODO: implementar" >&2
exit 1
