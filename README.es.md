# skillkit

[English](README.md) · **Español** · [中文](README.zh-CN.md) · [Deutsch](README.de.md) · [Français](README.fr.md)

Librería de **scripts reutilizables** que las skills pueden usar para actuar sobre su
sandbox. Cada script es una utilidad independiente con interfaz de línea de comandos,
pensada para copiarse a la carpeta `scripts/` de cualquier skill o para referenciarse
como dependencia común.

Estado: 13 scripts implementados que fijan el patrón, plantillas y generador para
replicarlo, suite de smoke tests, e índice (`catalog.json`) con **338 scripts en 23
categorías** (el resto como `planned`, priorizables por lotes).

## Estructura

```
skillkit/
├── README.md              # inglés (predeterminado) · también .es .zh-CN .de .fr
├── catalog.json           # índice machine-readable (lo genera build_catalog.py)
├── build_catalog.py       # regenera y VALIDA catalog.json
├── new-script             # genera un script nuevo desde plantilla
├── templates/             # template.bash y template.py (el patrón codificado)
├── tests/run_tests.sh     # smoke tests del repositorio
├── fs/                    # ficheros y búsqueda           → find-files ✓
├── text/                  # texto y datos estructurados
├── docs/                  # conversión de documentos y medios
├── containers/            # docker / k8s / openshift       → k8s-get, k8s-rbac-check ✓
├── web/                   # descarga y scraping            → web-to-markdown ✓
├── net/                   # red y diagnóstico
├── vcs/                   # git / mercurial / svn
├── forges/                # github / gitlab / etc.         → gh-issue ✓
├── pkg/                   # paquetes y dependencias
├── data/                  # bases de datos y datos         → xlsx-tool ✓
├── crypto/                # codificación / cripto / secretos
├── proc/                  # sistema, procesos, orquestación local
├── quality/               # tests, linting, calidad
├── api/                   # cliente HTTP/API genérico      → oauth-token ✓
├── cloud/                 # nubes e infraestructura        → coolify-api ✓
├── ai/                    # IA y LLMs                     → llm-call ✓
├── obs/                   # observabilidad
├── msg/                   # mensajería y notificaciones
├── store/                 # almacenamiento de objetos y backups
├── orch/                  # orquestadores de workflows     → kestra-flow ✓
├── validate/              # esquemas y políticas           → json-schema-validate ✓
├── sec/                   # seguridad y cadena de suministro → secret-scan, container-scan ✓
└── bench/                 # rendimiento
```

## Convenciones de diseño

1. **Salida**: los datos van por `stdout`; los mensajes y errores, por `stderr`.
2. **`--json`**: todo script que devuelve datos ofrece salida estructurada.
3. **`--help` siempre**: funciona aunque falte la herramienta base o las dependencias.
   En Python, el import de dependencias va dentro de `main()` por esta razón.
4. **Orden de comprobaciones**: validar argumentos (exit 2) *antes* de comprobar
   dependencias (exit 127). Un error de uso se reporta igual sin la herramienta.
5. **Dependencias en línea** (Python): PEP 723 + `uv run`; sin instalación previa.
6. **`--dry-run`** en toda operación que escribe o borra: imprime el comando exacto
   y **no requiere ni la herramienta ni credenciales** (previsualización universal).
7. **Códigos de salida**: `0` ok · `1` error de ejecución · `2` uso incorrecto ·
   `127` falta la herramienta (· `3` "sin resultado" en extractores).
8. **Sin secretos hardcodeados**: credenciales y tokens desde variables de entorno.
9. **Una responsabilidad por script**: hacer una cosa bien y componer.

## Scripts implementados

**`fs/find-files`** — buscar ficheros por nombre, tipo, extensión, fecha o tamaño.
```bash
find-files src --ext py --newer-than 7
find-files . --type d --name 'test*' --json
```

**`web/web-to-markdown`** — descargar una URL y extraer su contenido principal como
Markdown. PEP 723 (requiere `uv`); `--timeout` configurable. Si la descarga directa
falla, reintenta con la confianza TLS del sistema y los proxies de entorno, por lo
que funciona detrás de proxies corporativos con inspección TLS (Fortinet, Zscaler…).
```bash
uv run web/web-to-markdown https://example.com/post --json --timeout 20
```

**`containers/k8s-get`** — listar o describir recursos de Kubernetes/OpenShift.
La sonda de conectividad usa `/version` (legible por cualquier usuario autenticado),
por lo que funciona en clústeres con RBAC restringido donde `cluster-info` fallaría.
```bash
k8s-get pods -n falcone -l app=api --wide
KUBECTL=oc k8s-get deployment api -n falcone --json
```

**`forges/gh-issue`** — gestionar issues de GitHub. Token desde
`GH_TOKEN`/`GITHUB_TOKEN`; `--dry-run` imprime el comando exacto sin necesitar
`gh` ni token.
```bash
gh-issue list -R my-org/falcone -s open -l tenant-isolation --json
gh-issue create -R my-org/falcone -t "Fuga entre tenants" -b "Detalle…" --dry-run
```

**`validate/json-schema-validate`** — validar JSON/YAML (multi-documento) contra un
JSON Schema. Pensado para verificar salidas estructuradas de agentes antes de usarlas;
acepta `-` para leer de stdin. PEP 723 (requiere `uv`).
```bash
uv run validate/json-schema-validate ard.json --schema schemas/ard.schema.yaml
kestra-flow logs $EXEC | uv run validate/json-schema-validate - --schema out.json
```

**`ai/llm-call`** — llamar a un endpoint LLM y devolver la respuesta. Solo librería
estándar (sin instalación), confianza TLS del sistema, dialectos OpenAI-compatible y
Anthropic, reintentos ante 429/5xx. Sirve igual para endpoints privados (vLLM, Ollama,
LiteLLM) que para las APIs públicas. Config por `LLM_BASE_URL`/`LLM_MODEL`/`LLM_API_KEY`.
```bash
echo "Resume este BRD" | llm-call --system "Eres un arquitecto" --model qwen2 \
    --base-url http://vllm.interno:8000/v1 --json
```

**`orch/kestra-flow`** — validar, desplegar y ejecutar flujos de Kestra vía API REST.
`--wait` sigue la ejecución hasta su estado terminal; `--dry-run` muestra la llamada
sin servidor. Auth por token (EE/Cloud) o usuario/contraseña (OSS).
```bash
kestra-flow validate flows/ard-pipeline.yaml
kestra-flow execute prod brd-to-ard --input brd=s3://bucket/brd.xlsx --wait
```

**`data/xlsx-tool`** — inspeccionar y convertir Excel (`info`/`sheets`/`csv`/`json`).
`--sheet` por índice (1-based) o nombre. Útil para ingerir los BRD en Excel del
pipeline ARD. PEP 723 (requiere `uv`).
```bash
uv run data/xlsx-tool info brd.xlsx --json
uv run data/xlsx-tool json brd.xlsx --sheet Requisitos
```

**`containers/k8s-rbac-check`** — auditar permisos RBAC (`auth can-i`) en
Kubernetes/OpenShift. Soporta varios verbos, impersonación de usuario o ServiceAccount
y `--list`. Solo lectura. `KUBECTL=oc` para OpenShift.
```bash
k8s-rbac-check get,list,watch pods -n falcone --json
k8s-rbac-check delete secrets -n other-tenant --sa falcone:api   # ¿aislamiento ok?
```

**`api/oauth-token`** — obtener un token OAuth2 e imprimirlo (componible). Grants
`client_credentials`, `password`, `refresh_token` y `device` (flujo de dispositivo con
sondeo). Para Cognito, Keycloak, Auth0… `--auth-basic` envía las credenciales como
cabecera Basic; `--dry-run` muestra la petición con el secreto enmascarado.
```bash
TOKEN="$(oauth-token client_credentials --scope 'api/read' --auth-basic)"
oauth-token device --scope 'openid profile' --json
```

**`cloud/coolify-api`** — operar Coolify vía su API v4: listar aplicaciones, servicios
y bases de datos, y disparar `deploy`/`start`/`stop`/`restart`. Las operaciones de
escritura admiten `--dry-run` sin servidor. Config por `COOLIFY_URL`/`COOLIFY_TOKEN`.
```bash
coolify-api apps --json
coolify-api deploy 9b7c... --force
```

**`sec/secret-scan`** — buscar secretos filtrados con gitleaks (preferido) o trufflehog,
autodetectando la herramienta. Working tree por defecto o `--git-history` para el
historial completo. Devuelve exit 1 si hay hallazgos (apto para CI).
```bash
secret-scan . --git-history --json
secret-scan src --tool trufflehog --only-verified
```

**`sec/container-scan`** — escanear CVEs en imágenes o `--fs` con trivy (preferido) o
grype, autodetectando la herramienta. Umbral con `--severity`; exit 1 si hay
vulnerabilidades del nivel indicado.
```bash
container-scan registry.local/falcone-api:latest --severity CRITICAL,HIGH
container-scan --fs . --ignore-unfixed --json
```

## Tests

```bash
bash tests/run_tests.sh
```

Comprueba sintaxis, ayuda sin dependencias, errores de uso (exit 2), comportamiento
funcional (búsqueda con `--json`, `--dry-run` sin credenciales, generación desde
plantilla) y consistencia del catálogo. No requiere `gh` ni `kubectl`: verifica
justamente que los scripts degradan bien cuando faltan.

## Cómo añadir un script

```bash
./new-script text json-query bash -d "Consultar/transformar JSON" -b jq
```

1. Implementar la lógica en la sección 3 de la plantilla generada.
2. Añadir la entrada en `SCRIPTS` de `build_catalog.py` (y en `IMPLEMENTED` al acabar).
3. Regenerar el índice: `python3 build_catalog.py` (valida ids, categorías y ficheros).
4. Pasar la suite: `bash tests/run_tests.sh`.

## Cómo lo consume una skill

En el `SKILL.md`, apunta al script y describe cuándo usarlo; el código no entra en
contexto (progressive disclosure):

```markdown
## Convertir una página web a Markdown
Cuando necesites el contenido limpio de una URL, ejecuta:

    uv run scripts/web-to-markdown <URL> --json

Devuelve un objeto JSON con `title`, `author`, `date` y `markdown`.
```

Dos formas de incorporar la librería:
- **Copiar** el script suelto a `scripts/` de la skill (autocontenido).
- **Referenciar** este repo como dependencia común (p.ej. git submodule).

## Índice completo

`catalog.json` lista los 338 scripts con categoría, herramientas base, estado y, para
los implementados, flags, ejemplo de uso y notas. `build_catalog.py` lo regenera y
**falla con mensaje claro** si hay ids duplicados, categorías inválidas o scripts
marcados como implementados que no existen en disco.

## Notas

- Tras descomprimir, si el bit de ejecución no se conserva: `chmod +x <script>`.
- Los scripts Python con cabecera PEP 723 requieren `uv` (https://docs.astral.sh/uv/).
- `KUBECTL=oc` reutiliza los scripts de `containers/` en OpenShift.
- Antes de publicar el repositorio, añade una licencia (Apache-2.0 o MIT encajan con
  el ecosistema de skills).
