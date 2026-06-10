#!/usr/bin/env bash
#
# run_tests.sh — Smoke tests del repositorio skillkit.
# Uso: bash tests/run_tests.sh        (exit 0 si todo pasa)
#
# No requiere herramientas externas (gh, kubectl…): comprueba precisamente
# que los scripts se comportan bien también cuando estas faltan.

set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT" || exit 1

PASS=0
FAIL=0
ok() { echo "  ok    $1"; PASS=$((PASS + 1)); }
ko() { echo "  FAIL  $1"; FAIL=$((FAIL + 1)); }

# expect_exit DESC CODIGO_ESPERADO CMD...
expect_exit() {
  local desc="$1" want="$2"; shift 2
  local got=0
  "$@" >/dev/null 2>&1 || got=$?
  if [[ "$got" -eq "$want" ]]; then ok "$desc"; else ko "$desc (exit $got, esperado $want)"; fi
}

echo "== 1. Sintaxis =="
for s in fs/find-files containers/k8s-get forges/gh-issue new-script tests/run_tests.sh \
         orch/kestra-flow containers/k8s-rbac-check \
         api/oauth-token cloud/coolify-api sec/secret-scan sec/container-scan; do
  if bash -n "$s" 2>/dev/null; then ok "bash -n $s"; else ko "bash -n $s"; fi
done
if python3 -m py_compile web/web-to-markdown build_catalog.py \
     ai/llm-call validate/json-schema-validate data/xlsx-tool 2>/dev/null; then
  ok "py_compile (scripts python)"
else
  ko "py_compile (scripts python)"
fi
find . -name '__pycache__' -type d -prune -exec rm -rf {} + 2>/dev/null

echo "== 2. Ayuda sin dependencias instaladas =="
expect_exit "find-files --help"        0 bash fs/find-files --help
expect_exit "k8s-get --help"           0 bash containers/k8s-get --help
expect_exit "gh-issue --help"          0 bash forges/gh-issue --help
expect_exit "web-to-markdown --help"   0 python3 web/web-to-markdown --help
expect_exit "new-script --help"        0 bash new-script --help
expect_exit "json-schema-validate --help" 0 python3 validate/json-schema-validate --help
expect_exit "llm-call --help"          0 python3 ai/llm-call --help
expect_exit "xlsx-tool --help"         0 python3 data/xlsx-tool --help
expect_exit "kestra-flow --help"       0 bash orch/kestra-flow --help
expect_exit "k8s-rbac-check --help"    0 bash containers/k8s-rbac-check --help
expect_exit "oauth-token --help"       0 bash api/oauth-token --help
expect_exit "coolify-api --help"       0 bash cloud/coolify-api --help
expect_exit "secret-scan --help"       0 bash sec/secret-scan --help
expect_exit "container-scan --help"    0 bash sec/container-scan --help

echo "== 3. Errores de uso (exit 2, sin exigir la herramienta) =="
expect_exit "find-files --type invalido"     2 bash fs/find-files . --type x
expect_exit "k8s-get sin recurso"            2 bash containers/k8s-get
expect_exit "k8s-get --json --describe"      2 bash containers/k8s-get pods --json --describe
expect_exit "gh-issue sin subcomando"        2 bash forges/gh-issue
expect_exit "gh-issue create sin --title"    2 bash forges/gh-issue create
expect_exit "web-to-markdown sin URL"        2 python3 web/web-to-markdown
expect_exit "new-script sin argumentos"      2 bash new-script
expect_exit "json-schema-validate sin --schema" 2 python3 validate/json-schema-validate algo.json
expect_exit "llm-call sin prompt"            2 sh -c 'python3 ai/llm-call --model x </dev/null'
expect_exit "kestra-flow execute incompleto" 2 bash orch/kestra-flow execute soloNS
expect_exit "kestra-flow subcomando malo"    2 bash orch/kestra-flow frobnicate
expect_exit "k8s-rbac-check sin recurso"     2 bash containers/k8s-rbac-check get
expect_exit "k8s-rbac-check --sa mal formato" 2 bash containers/k8s-rbac-check get pods --sa malo
expect_exit "xlsx-tool comando inválido"     2 python3 data/xlsx-tool frobnicate f.xlsx
expect_exit "oauth-token sin grant"          2 bash api/oauth-token
expect_exit "oauth-token grant inválido"     2 bash api/oauth-token frobnicate
expect_exit "oauth-token password incompleto" 2 bash api/oauth-token password
expect_exit "coolify-api sin subcomando"     2 bash cloud/coolify-api
expect_exit "coolify-api deploy sin UUID"    2 bash cloud/coolify-api deploy
expect_exit "coolify-api subcomando malo"    2 bash cloud/coolify-api frobnicate
expect_exit "secret-scan --tool inválida"    2 bash sec/secret-scan --tool xxx
expect_exit "container-scan sin objetivo"    2 bash sec/container-scan
expect_exit "container-scan imagen + --fs"   2 bash sec/container-scan img --fs .

echo "== 3b. Contrato de herramienta ausente (exit 127) =="
expect_exit "k8s-get sin kubectl"            127 env KUBECTL=__no_such_tool__ bash containers/k8s-get pods
expect_exit "k8s-rbac-check sin kubectl"     127 env KUBECTL=__no_such_tool__ bash containers/k8s-rbac-check get pods
expect_exit "llm-call --api anthropic sin modelo" 2 env -u LLM_MODEL python3 ai/llm-call --api anthropic hola

echo "== 4. Funcional =="
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
touch "$TMP/a.py" "$TMP/b.py" "$TMP/c.txt"
if bash fs/find-files "$TMP" --ext py --json 2>/dev/null \
   | python3 -c 'import sys,json; sys.exit(0 if len(json.load(sys.stdin)) == 2 else 1)'; then
  ok "find-files --json devuelve los 2 .py"
else
  ko "find-files --json devuelve los 2 .py"
fi

DRYERR="$(bash forges/gh-issue create -R demo/repo -t "Prueba" --dry-run 2>&1 1>/dev/null)"
DRYRC=$?
if [[ "$DRYRC" -eq 0 && "$DRYERR" == *"[dry-run]"* ]]; then
  ok "gh-issue --dry-run funciona sin 'gh' ni token"
else
  ko "gh-issue --dry-run funciona sin 'gh' ni token (exit $DRYRC)"
fi

bash new-script text zz-test-tmp bash -d "Demo" -b echo >/dev/null 2>&1
GENRC=$?
if [[ "$GENRC" -eq 0 && -f "text/zz-test-tmp" ]] \
   && bash -n text/zz-test-tmp 2>/dev/null \
   && bash text/zz-test-tmp --help >/dev/null 2>&1; then
  ok "new-script genera un script válido desde plantilla"
else
  ko "new-script genera un script válido desde plantilla (exit $GENRC)"
fi
rm -f text/zz-test-tmp
expect_exit "new-script rechaza sobrescribir" 1 bash new-script fs find-files bash

echo "== 4b. Funcional (lote nuevo) =="
# json-schema-validate: requiere uv (deps PEP 723). Si no hay uv, se omite.
if command -v uv >/dev/null 2>&1; then
  SCHEMA="$TMP/schema.json"; cat > "$SCHEMA" <<'JSON'
{ "type": "object", "required": ["name", "version"],
  "properties": { "name": {"type": "string"}, "version": {"type": "string"} } }
JSON
  echo '{"name":"demo","version":"1.0"}' > "$TMP/ok.json"
  echo '{"name":"demo"}'                  > "$TMP/bad.json"
  if uv run --script validate/json-schema-validate "$TMP/ok.json" --schema "$SCHEMA" >/dev/null 2>&1; then
    ok "json-schema-validate acepta documento válido (exit 0)"
  else
    ko "json-schema-validate acepta documento válido (exit 0)"
  fi
  RC=0; uv run --script validate/json-schema-validate "$TMP/bad.json" --schema "$SCHEMA" >/dev/null 2>&1 || RC=$?
  if [[ "$RC" -eq 1 ]]; then ok "json-schema-validate rechaza inválido (exit 1)"; else ko "json-schema-validate rechaza inválido (exit 1, fue $RC)"; fi

  # xlsx-tool: construir un libro mínimo con openpyxl y verificar el volcado.
  XLSX="$TMP/demo.xlsx"
  if uv run --with 'openpyxl>=3.1' python - "$XLSX" <<'PY' >/dev/null 2>&1
import sys, openpyxl
wb = openpyxl.Workbook(); ws = wb.active; ws.title = "Datos"
ws.append(["id", "nombre"]); ws.append([1, "uno"]); ws.append([2, "dos"])
wb.save(sys.argv[1])
PY
  then
    CSV="$(uv run --script data/xlsx-tool csv "$XLSX" --sheet Datos 2>/dev/null | tr -d '\r')"
    if [[ "$(printf '%s' "$CSV" | head -1)" == "id,nombre" ]]; then
      ok "xlsx-tool csv vuelca la hoja con cabecera"
    else
      ko "xlsx-tool csv vuelca la hoja con cabecera"
    fi
    N="$(uv run --script data/xlsx-tool json "$XLSX" --sheet 1 2>/dev/null | python3 -c 'import json,sys; print(len(json.load(sys.stdin)))')"
    if [[ "$N" == "2" ]]; then ok "xlsx-tool json devuelve 2 registros"; else ko "xlsx-tool json devuelve 2 registros (fue $N)"; fi
  else
    echo "  skip  xlsx-tool (no se pudo crear el libro de prueba)"
  fi
else
  echo "  skip  json-schema-validate / xlsx-tool (uv no disponible)"
fi

# Dry-runs: deben funcionar sin servidor ni credenciales y devolver 0.
printf 'id: demo\nnamespace: test\n' > "$TMP/flow.yaml"
DRYK="$(bash orch/kestra-flow deploy "$TMP/flow.yaml" --dry-run 2>&1 1>/dev/null)"; KRC=$?
if [[ "$KRC" -eq 0 && "$DRYK" == *"[dry-run]"* ]]; then
  ok "kestra-flow deploy --dry-run sin servidor"
else
  ko "kestra-flow deploy --dry-run sin servidor (exit $KRC)"
fi

# oauth-token: dry-run sin endpoint/curl, y el secreto debe ir enmascarado.
OUT="$(OAUTH_CLIENT_ID=app OAUTH_CLIENT_SECRET=supersecreto \
        bash api/oauth-token client_credentials --scope api/read --dry-run 2>&1)"; ORC=$?
if [[ "$ORC" -eq 0 && "$OUT" == *"client_secret=***"* && "$OUT" != *"supersecreto"* ]]; then
  ok "oauth-token --dry-run enmascara el secreto"
else
  ko "oauth-token --dry-run enmascara el secreto (exit $ORC)"
fi

# coolify-api: operación de escritura en dry-run sin COOLIFY_URL.
OUT="$(bash cloud/coolify-api deploy demo-uuid --force --dry-run 2>&1)"; CRC=$?
if [[ "$CRC" -eq 0 && "$OUT" == *"/api/v1/deploy?uuid=demo-uuid&force=true"* ]]; then
  ok "coolify-api deploy --dry-run sin servidor"
else
  ko "coolify-api deploy --dry-run sin servidor (exit $CRC)"
fi

# secret-scan / container-scan: dry-run muestra el comando sin la herramienta.
OUT="$(bash sec/secret-scan . --dry-run 2>&1)"; SRC=$?
if [[ "$SRC" -eq 0 && "$OUT" == *"gitleaks detect"* ]]; then
  ok "secret-scan --dry-run sin la herramienta"
else
  ko "secret-scan --dry-run sin la herramienta (exit $SRC)"
fi
OUT="$(bash sec/container-scan img:latest --dry-run 2>&1)"; VRC=$?
if [[ "$VRC" -eq 0 && "$OUT" == *"trivy image img:latest"* ]]; then
  ok "container-scan --dry-run sin la herramienta"
else
  ko "container-scan --dry-run sin la herramienta (exit $VRC)"
fi

echo "== 5. Cobertura del catálogo (TODOS los scripts implementados) =="
# Recorre cada script marcado 'implemented' en catalog.json y verifica que
# existe, su sintaxis y que '--help' funciona sin dependencias. El intérprete
# se deduce del shebang. Los scripts 'planned' aún no tienen fichero, así que
# no se prueban aquí; esta sección crece sola al implementar nuevos lotes.
EXPECTED_IMPL="$(python3 -c 'import json,sys; sys.stdout.write(str(sum(1 for s in json.load(open("catalog.json","r",encoding="utf-8"))["scripts"] if s["status"]=="implemented")))')"
COVERED=0
while IFS= read -r path; do
  [ -z "$path" ] && continue
  if [ ! -f "$path" ]; then ko "cobertura: falta el fichero $path"; continue; fi
  shebang="$(head -n1 "$path" 2>/dev/null)"
  case "$shebang" in
    *python*|*uv*)
      if python3 -m py_compile "$path" 2>/dev/null && python3 "$path" --help >/dev/null 2>&1; then
        ok "cobertura $path (python: compila + --help)"; COVERED=$((COVERED + 1))
      else
        ko "cobertura $path (python: compila + --help)"
      fi ;;
    *bash*)
      if bash -n "$path" 2>/dev/null && bash "$path" --help >/dev/null 2>&1; then
        ok "cobertura $path (bash: -n + --help)"; COVERED=$((COVERED + 1))
      else
        ko "cobertura $path (bash: -n + --help)"
      fi ;;
    *)
      ko "cobertura $path (shebang no reconocido)" ;;
  esac
done < <(python3 -c 'import json
for s in json.load(open("catalog.json","r",encoding="utf-8"))["scripts"]:
    if s["status"] == "implemented":
        print(s["path"])')
find . -name '__pycache__' -type d -prune -exec rm -rf {} + 2>/dev/null
if [[ "$COVERED" -gt 0 && "$COVERED" -eq "$EXPECTED_IMPL" ]]; then
  ok "cobertura completa: $COVERED/$EXPECTED_IMPL scripts implementados probados"
else
  ko "cobertura completa: $COVERED/$EXPECTED_IMPL scripts implementados probados"
fi

echo "== 6. Consistencia del catálogo =="
if python3 build_catalog.py >/dev/null 2>&1 && python3 -m json.tool catalog.json >/dev/null 2>&1; then
  ok "build_catalog.py valida y genera JSON correcto"
else
  ko "build_catalog.py valida y genera JSON correcto"
fi
if python3 - <<'PY'
import json, os, sys
cat = json.load(open("catalog.json", encoding="utf-8"))
bad = [s["path"] for s in cat["scripts"] if s["status"] == "implemented" and not os.path.isfile(s["path"])]
sys.exit(1 if bad else 0)
PY
then
  ok "todos los 'implemented' existen en disco"
else
  ko "todos los 'implemented' existen en disco"
fi

echo
echo "Resultado: $PASS ok, $FAIL fallos"
[[ "$FAIL" -eq 0 ]]
