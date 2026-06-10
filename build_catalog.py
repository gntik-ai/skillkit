#!/usr/bin/env python3
"""Genera catalog.json, el índice machine-readable de scripts del repositorio.

Mantener los datos aquí (tuplas compactas) y regenerar con:

    python3 build_catalog.py

Un agente puede leer catalog.json para descubrir qué scripts existen, en qué
estado están y cómo invocarlos.
"""
from __future__ import annotations

import json
from pathlib import Path

VERSION = "0.2.0"

CATEGORIES: list[tuple[str, str]] = [
    ("fs", "Sistema de ficheros y búsqueda"),
    ("text", "Texto y datos estructurados"),
    ("docs", "Conversión de documentos y medios"),
    ("containers", "Contenedores y orquestación"),
    ("web", "Descarga y scraping web"),
    ("net", "Red y diagnóstico"),
    ("vcs", "Control de versiones"),
    ("forges", "Plataformas de repositorios"),
    ("pkg", "Paquetes y dependencias"),
    ("data", "Bases de datos y datos"),
    ("crypto", "Codificación, criptografía y secretos"),
    ("proc", "Sistema, procesos y orquestación local"),
    ("quality", "Pruebas, linting y calidad"),
    ("api", "Cliente HTTP / API genérico"),
    ("cloud", "Nubes e infraestructura"),
    ("ai", "IA y LLMs"),
    ("obs", "Observabilidad"),
    ("msg", "Mensajería y notificaciones"),
    ("store", "Almacenamiento de objetos y backups"),
    ("orch", "Orquestadores de workflows"),
    ("validate", "Esquemas y políticas"),
    ("sec", "Seguridad y cadena de suministro"),
    ("bench", "Rendimiento"),
]

# (id, category, [herramientas base], descripción)
SCRIPTS: list[tuple[str, str, list[str], str]] = [
    # fs
    ("find-files", "fs", ["fd", "find"], "Buscar ficheros por nombre, tipo, extensión, fecha o tamaño"),
    ("search-content", "fs", ["ripgrep", "grep"], "Buscar texto o regex en un árbol de ficheros"),
    ("safe-delete", "fs", ["trash-cli"], "Borrar a la papelera en vez de rm -rf (reversible)"),
    ("bulk-rename", "fs", ["rename", "mmv"], "Renombrar en lote por patrón o regex"),
    ("tree-view", "fs", ["eza", "tree"], "Listar el árbol de directorios filtrando ruido"),
    ("file-type", "fs", ["file"], "Detectar el tipo/MIME real de un fichero"),
    ("dedupe-files", "fs", ["fdupes", "jdupes"], "Encontrar o eliminar duplicados por hash"),
    ("disk-usage", "fs", ["dust", "du"], "Uso de disco por carpeta, ordenado"),
    ("archive", "fs", ["tar", "unzip", "7z"], "Comprimir/descomprimir detectando el formato"),
    ("sync-dir", "fs", ["rsync"], "Copiar/sincronizar incremental con filtros"),
    ("watch-files", "fs", ["watchexec", "entr"], "Ejecutar un comando al cambiar ficheros"),
    ("chmod-tree", "fs", ["chmod", "chown"], "Fijar permisos/propietario recursivos seguros"),
    # text
    ("json-query", "text", ["jq"], "Consultar/transformar JSON"),
    ("yaml-query", "text", ["yq"], "Leer/editar YAML"),
    ("xml-query", "text", ["xmlstarlet", "xmllint"], "Consultar/validar XML"),
    ("csv-tool", "text", ["csvkit", "miller"], "Filtrar/unir/convertir/estadísticas de CSV"),
    ("toml-tool", "text", ["tomlq", "dasel"], "Leer/editar TOML"),
    ("multi-query", "text", ["dasel"], "Consultar JSON/YAML/TOML/XML con una sola sintaxis"),
    ("text-extract", "text", ["grep", "sed", "awk"], "Extraer por regex o por campos"),
    ("diff-text", "text", ["delta", "diff", "patch"], "Diff legible y aplicación de parches"),
    ("dedupe-lines", "text", ["sort", "uniq"], "Ordenar/uniq/contar líneas"),
    ("encoding-convert", "text", ["iconv"], "Convertir codificación/charset"),
    ("template-render", "text", ["envsubst", "jinja2-cli"], "Rellenar plantillas con variables"),
    # docs
    ("doc-convert", "docs", ["pandoc"], "Convertir entre md/html/docx/pdf/rst"),
    ("office-convert", "docs", ["libreoffice"], "Conversión office headless (docx→pdf, xlsx→csv…)"),
    ("pdf-text", "docs", ["pdftotext", "pdfplumber"], "Extraer texto/tablas de un PDF"),
    ("pdf-ops", "docs", ["qpdf", "pdftk"], "Unir/dividir/rotar/recortar PDF"),
    ("pdf-ocr", "docs", ["ocrmypdf", "tesseract"], "OCR sobre PDF o imagen escaneada"),
    ("img-convert", "docs", ["imagemagick", "cwebp"], "Convertir/redimensionar/optimizar imágenes"),
    ("media-transcode", "docs", ["ffmpeg"], "Convertir/recortar audio y vídeo"),
    ("exif-tool", "docs", ["exiftool"], "Leer o limpiar metadatos de ficheros"),
    # containers
    ("docker-build", "containers", ["docker"], "Construir imagen con cache y tags"),
    ("docker-run", "containers", ["docker"], "Ejecutar contenedor efímero con limpieza"),
    ("docker-logs", "containers", ["docker"], "Seguir logs / exec / inspect"),
    ("docker-prune", "containers", ["docker"], "Limpiar imágenes/volúmenes/redes huérfanas"),
    ("compose-up", "containers", ["docker compose"], "Levantar/parar/logs de un stack"),
    ("podman-run", "containers", ["podman"], "Equivalente rootless a docker"),
    ("k8s-get", "containers", ["kubectl"], "Listar o describir recursos de Kubernetes/OpenShift"),
    ("k8s-logs", "containers", ["kubectl"], "Logs / exec / port-forward de pods"),
    ("k8s-apply", "containers", ["kubectl"], "Aplicar y hacer diff de manifiestos"),
    ("k8s-rollout", "containers", ["kubectl"], "Desplegar y vigilar rollout/status"),
    ("k8s-context", "containers", ["kubectx", "kubens"], "Cambiar contexto/namespace de forma segura"),
    ("helm-deploy", "containers", ["helm"], "Instalar/actualizar/plantilla de charts"),
    ("kustomize-build", "containers", ["kustomize"], "Renderizar overlays"),
    ("oc-tool", "containers", ["oc"], "Operaciones OpenShift (proyectos, rutas, builds)"),
    ("local-cluster", "containers", ["kind", "minikube"], "Crear un clúster local efímero para pruebas"),
    # web
    ("fetch-url", "web", ["curl", "wget"], "Descargar con reintentos/resume/headers"),
    ("http-request", "web", ["httpie", "curl"], "Cliente REST legible (GET/POST/JSON)"),
    ("web-to-markdown", "web", ["trafilatura"], "Extraer el contenido principal de una URL como Markdown"),
    ("html-parse", "web", ["pup", "beautifulsoup4"], "Extraer nodos por selector CSS"),
    ("render-page", "web", ["playwright", "puppeteer"], "Renderizar páginas con JS y extraer el DOM"),
    ("screenshot-page", "web", ["playwright"], "Captura de pantalla de una URL"),
    ("crawl-site", "web", ["wget", "scrapy"], "Recorrer sitemap/enlaces con límite de profundidad"),
    ("download-batch", "web", ["aria2c", "curl"], "Descargar una lista de URLs en paralelo"),
    # net
    ("dns-lookup", "net", ["dig", "host"], "Resolver A/AAAA/MX/TXT/CNAME"),
    ("ping-host", "net", ["ping", "fping"], "Comprobar alcanzabilidad y latencia"),
    ("trace-route", "net", ["mtr", "traceroute"], "Trazar la ruta de red"),
    ("port-check", "net", ["nc", "ss"], "Comprobar si un puerto está abierto/escuchando"),
    ("wait-for", "net", ["wait-for-it", "nc"], "Esperar a que un host:puerto responda"),
    ("tls-inspect", "net", ["openssl"], "Inspeccionar/verificar certificado y handshake TLS"),
    ("whois-lookup", "net", ["whois"], "Datos de dominio/IP"),
    ("http-status", "net", ["curl"], "Estado/cabeceras/redirecciones de una URL"),
    ("ssh-run", "net", ["ssh"], "Ejecutar comando remoto o abrir túnel"),
    ("rsync-remote", "net", ["rsync"], "Copiar a/desde un host remoto"),
    # vcs
    ("git-clone", "vcs", ["git"], "Clonar (shallow / sparse checkout)"),
    ("git-status", "vcs", ["git"], "Estado / diff / log resumido"),
    ("git-commit", "vcs", ["git"], "Commit con mensaje (Conventional Commits)"),
    ("git-branch", "vcs", ["git"], "Crear/cambiar/limpiar ramas"),
    ("git-blame", "vcs", ["git"], "Autoría por línea o rango"),
    ("git-history", "vcs", ["git"], "Log gráfico o por fichero"),
    ("git-rewrite", "vcs", ["git-filter-repo"], "Reescribir/filtrar historial"),
    ("conventional-commit", "vcs", ["commitlint", "commitizen"], "Validar/generar mensajes Conventional Commits"),
    ("changelog-gen", "vcs", ["git-cliff"], "Generar CHANGELOG desde commits/tags"),
    ("hg-tool", "vcs", ["hg"], "Clonar/log/commit en Mercurial"),
    ("svn-tool", "vcs", ["svn"], "Checkout/diff/commit en Subversion"),
    ("repo-stats", "vcs", ["git-quick-stats"], "Métricas de actividad y contribuidores"),
    # forges
    ("gh-repo", "forges", ["gh"], "Crear/clonar/ver repos de GitHub"),
    ("gh-issue", "forges", ["gh"], "Gestionar issues de GitHub (list/view/create/comment/close/reopen)"),
    ("gh-pr", "forges", ["gh"], "Abrir/revisar/mergear pull requests"),
    ("gh-release", "forges", ["gh"], "Crear releases y subir artefactos"),
    ("gh-workflow", "forges", ["gh"], "Disparar/ver runs de GitHub Actions"),
    ("gh-api", "forges", ["gh"], "Llamadas REST/GraphQL autenticadas a GitHub"),
    ("glab-mr", "forges", ["glab"], "Merge requests en GitLab"),
    ("glab-issue", "forges", ["glab"], "Issues en GitLab"),
    ("glab-ci", "forges", ["glab"], "Pipelines de GitLab CI"),
    ("gitea-api", "forges", ["curl"], "Operaciones contra Gitea/Forgejo vía API"),
    ("bitbucket-api", "forges", ["curl"], "Operaciones contra Bitbucket vía API"),
    ("repo-mirror", "forges", ["git"], "Mirror/push entre remotos"),
    # pkg
    ("py-install", "pkg", ["uv", "pipx", "pip"], "Instalar dependencias Python aisladas y rápidas"),
    ("node-install", "pkg", ["pnpm", "npm", "yarn"], "Instalar dependencias Node"),
    ("rust-build", "pkg", ["cargo"], "Compilar/test en Rust"),
    ("apt-install", "pkg", ["apt-get"], "Instalar paquetes de sistema"),
    ("dep-audit", "pkg", ["pip-audit", "npm", "osv-scanner"], "Auditar vulnerabilidades de dependencias"),
    ("lock-diff", "pkg", ["git", "jq"], "Comparar cambios en lockfiles"),
    ("venv-setup", "pkg", ["uv", "python"], "Crear/activar un entorno virtual"),
    # data
    ("sqlite-query", "data", ["sqlite3"], "Ejecutar SQL sobre SQLite y formatear la salida"),
    ("psql-query", "data", ["psql"], "Consultar PostgreSQL"),
    ("mysql-query", "data", ["mysql"], "Consultar MySQL/MariaDB"),
    ("redis-cmd", "data", ["redis-cli"], "Operaciones sobre Redis"),
    ("mongo-query", "data", ["mongosh"], "Consultar MongoDB"),
    ("db-dump", "data", ["pg_dump", "mysqldump"], "Backup/restore de base de datos"),
    ("data-profile", "data", ["duckdb", "pandas"], "Estadísticas rápidas de CSV/parquet"),
    ("sql-format", "data", ["sqlfluff"], "Formatear/validar/lint SQL"),
    # crypto
    ("base-encode", "crypto", ["base64", "xxd"], "base64 / hex encode-decode"),
    ("hash-file", "crypto", ["sha256sum"], "Calcular/verificar checksums"),
    ("openssl-enc", "crypto", ["openssl"], "Cifrar/descifrar/firmar"),
    ("gpg-tool", "crypto", ["gpg"], "Cifrado y firma GPG"),
    ("jwt-decode", "crypto", ["jwt-cli", "jq"], "Decodificar/validar JWT"),
    ("uuid-gen", "crypto", ["uuidgen"], "Generar UUID/ULID"),
    ("secret-gen", "crypto", ["openssl", "pwgen"], "Generar contraseñas/tokens seguros"),
    ("redact-secrets", "crypto", ["gitleaks"], "Detectar/enmascarar secretos en texto o logs"),
    ("env-secrets", "crypto", ["dotenv"], "Cargar secretos desde .env de forma segura"),
    # proc
    ("run-bg", "proc", ["setsid", "nohup"], "Lanzar proceso en background con PID y log"),
    ("retry", "proc", ["retry"], "Reintentar un comando con backoff"),
    ("timeout-cmd", "proc", ["timeout"], "Limitar la duración de un comando"),
    ("parallel-run", "proc", ["parallel", "xargs"], "Ejecutar tareas en paralelo"),
    ("env-manager", "proc", ["direnv"], "Gestionar variables/entorno por proyecto"),
    ("proc-info", "proc", ["ps", "procps"], "Snapshot de procesos y recursos"),
    ("schedule", "proc", ["cron", "at"], "Programar tareas"),
    ("log-tail", "proc", ["lnav", "tail"], "Seguir/filtrar logs con color y navegación"),
    # quality
    ("lint-py", "quality", ["ruff", "black"], "Formatear y lint de Python"),
    ("lint-js", "quality", ["eslint", "prettier"], "Formatear y lint de JS/TS"),
    ("run-tests", "quality", ["pytest", "jest"], "Ejecutar suites de test"),
    ("coverage", "quality", ["coverage.py", "nyc"], "Medir cobertura de tests"),
    ("type-check", "quality", ["mypy", "tsc"], "Comprobación de tipos"),
    ("sast-scan", "quality", ["semgrep"], "Análisis estático de seguridad"),
    ("spell-check", "quality", ["codespell"], "Ortografía en código y docs"),
    # api
    ("api-call", "api", ["curl"], "Llamada REST autenticada (token desde entorno)"),
    ("api-paginate", "api", ["curl", "jq"], "Recorrer endpoints paginados"),
    ("api-retry", "api", ["curl"], "Reintentos/backoff ante 429/5xx"),
    ("normalize-response", "api", ["jq", "miller"], "Pasar respuestas a JSON/CSV plano"),
    ("openapi-client", "api", ["openapi-generator"], "Generar un cliente desde una spec OpenAPI"),
    ("webhook-send", "api", ["curl"], "Enviar payloads a un webhook"),
    ("graphql-query", "api", ["curl", "jq"], "Ejecutar consultas GraphQL"),
    # cloud
    ("aws-cli", "cloud", ["aws"], "Operaciones AWS"),
    ("gcloud-cli", "cloud", ["gcloud"], "Operaciones GCP"),
    ("az-cli", "cloud", ["az"], "Operaciones Azure"),
    ("terraform", "cloud", ["terraform"], "Plan/apply de infraestructura como código"),
    ("ansible-run", "cloud", ["ansible-playbook"], "Ejecutar playbooks"),
    # ── Ampliación v0.2 · categorías nuevas ──────────────────────────────
    # ai
    ("llm-call", "ai", ["curl", "python"], "Llamada a un endpoint LLM compatible OpenAI/Anthropic (prompt, system, temperatura)"),
    ("embed-text", "ai", ["sentence-transformers", "curl"], "Generar embeddings de textos o ficheros"),
    ("vector-upsert", "ai", ["python"], "Insertar vectores con metadatos en Pinecone/Qdrant/pgvector"),
    ("vector-search", "ai", ["python"], "Búsqueda semántica en el índice vectorial"),
    ("rag-chunk", "ai", ["python"], "Trocear documentos en chunks con solape y metadatos para RAG"),
    ("tokens-count", "ai", ["tiktoken"], "Contar tokens de un texto para un modelo dado"),
    ("whisper-transcribe", "ai", ["whisper.cpp", "curl"], "Audio a texto con timestamps"),
    ("tts-speak", "ai", ["curl"], "Texto a audio (voz, idioma, formato) vía Azure/Google/ElevenLabs"),
    ("image-caption", "ai", ["curl"], "Describir o extraer información de una imagen (visión)"),
    ("translate-text", "ai", ["curl", "argos-translate"], "Traducir preservando formato Markdown/HTML"),
    ("moderation-check", "ai", ["curl"], "Clasificar contenido contra políticas de seguridad"),
    ("ollama-tool", "ai", ["ollama"], "Descargar y ejecutar modelos locales"),
    ("hf-download", "ai", ["huggingface-cli"], "Descargar modelos/datasets de Hugging Face con filtros"),
    ("prompt-eval", "ai", ["promptfoo"], "Evaluar prompts contra casos de test con aserciones"),
    # obs
    ("prom-query", "obs", ["promtool", "curl"], "Consultas PromQL instantáneas o de rango"),
    ("loki-query", "obs", ["logcli"], "Consultas LogQL sobre Loki"),
    ("elastic-query", "obs", ["curl"], "Buscar en Elasticsearch/OpenSearch (DSL o KQL)"),
    ("grafana-api", "obs", ["curl"], "Dashboards, anotaciones y snapshots de Grafana"),
    ("alert-silence", "obs", ["amtool"], "Crear/listar/expirar silencios en Alertmanager"),
    ("jaeger-trace", "obs", ["curl"], "Buscar y descargar trazas distribuidas"),
    ("otel-emit", "obs", ["otel-cli"], "Emitir trazas/métricas/logs de prueba OTLP"),
    ("sentry-api", "obs", ["sentry-cli"], "Issues, releases y sourcemaps en Sentry"),
    ("uptime-check", "obs", ["curl"], "Disponibilidad de varios endpoints con umbrales y reporte"),
    ("metrics-scrape", "obs", ["curl"], "Raspar un endpoint /metrics y convertirlo a JSON"),
    # msg
    ("kafka-tool", "msg", ["kcat"], "Producir/consumir/inspeccionar topics y offsets"),
    ("rabbitmq-tool", "msg", ["rabbitmqadmin"], "Publicar/consumir y gestionar colas y exchanges"),
    ("nats-tool", "msg", ["nats"], "Pub/sub y streams JetStream"),
    ("mqtt-tool", "msg", ["mosquitto_pub", "mosquitto_sub"], "Publicar/suscribir MQTT (IoT)"),
    ("smtp-send", "msg", ["msmtp", "swaks"], "Enviar email con adjuntos/HTML contra cualquier SMTP"),
    ("imap-fetch", "msg", ["python"], "Leer/buscar/descargar de un buzón IMAP"),
    ("slack-post", "msg", ["curl"], "Mensajes y ficheros a Slack (webhook o API)"),
    ("telegram-send", "msg", ["curl"], "Mensajes/ficheros vía bot de Telegram"),
    ("discord-post", "msg", ["curl"], "Webhook de Discord"),
    ("teams-post", "msg", ["curl"], "Webhook/Adaptive Cards de Teams"),
    ("sms-send", "msg", ["curl"], "SMS vía Twilio u otro proveedor"),
    ("push-notify", "msg", ["ntfy", "gotify"], "Notificación push autoalojada"),
    ("ics-tool", "msg", ["python"], "Crear/parsear eventos e invitaciones .ics"),
    # store
    ("s3-tool", "store", ["aws", "mc"], "Subir/bajar/listar/presign en S3 y compatibles (MinIO)"),
    ("gcs-tool", "store", ["gsutil"], "Operaciones en Google Cloud Storage"),
    ("azblob-tool", "store", ["az"], "Operaciones en Azure Blob"),
    ("rclone-sync", "store", ["rclone"], "Sincronizar con 70+ backends (Drive, FTP, S3, B2…)"),
    ("sftp-tool", "store", ["lftp"], "Transferencias SFTP/FTPS scriptables con mirror"),
    ("webdav-tool", "store", ["curl"], "Subir/bajar vía WebDAV (Nextcloud, ownCloud)"),
    ("restic-backup", "store", ["restic"], "Backups cifrados y desduplicados, restore y prune"),
    ("snapshot-dir", "store", ["tar", "rsync"], "Snapshot incremental de un directorio con retención"),
    # orch
    ("kestra-flow", "orch", ["kestra", "curl"], "Validar/desplegar/ejecutar flujos de Kestra y seguir ejecuciones"),
    ("airflow-dag", "orch", ["airflow", "curl"], "Disparar DAGs, estado de runs, pausar/reanudar"),
    ("temporal-tool", "orch", ["temporal"], "Workflows y task queues de Temporal"),
    ("n8n-api", "orch", ["curl"], "Activar workflows y consultar ejecuciones en n8n"),
    ("prefect-run", "orch", ["prefect"], "Lanzar y monitorizar flows de Prefect"),
    # validate
    ("json-schema-validate", "validate", ["check-jsonschema"], "Validar JSON/YAML contra JSON Schema (salidas de agentes incluidas)"),
    ("openapi-lint", "validate", ["spectral", "redocly"], "Lint y validación de especificaciones OpenAPI"),
    ("k8s-validate", "validate", ["kubeconform"], "Validar manifiestos contra el esquema del clúster, offline"),
    ("kyverno-test", "validate", ["kyverno"], "Probar manifiestos contra políticas Kyverno antes de aplicar"),
    ("conftest-policy", "validate", ["conftest"], "Políticas OPA/Rego sobre cualquier configuración"),
    ("gha-lint", "validate", ["actionlint"], "Lint de workflows de GitHub Actions"),
    ("ci-lint", "validate", ["glab"], "Validar .gitlab-ci.yml contra la instancia"),
    ("compose-validate", "validate", ["docker compose"], "Validar y resolver docker-compose con interpolación"),
    ("regex-test", "validate", ["python"], "Probar una regex contra muestras con grupos explicados"),
    ("format-validate", "validate", ["python"], "Validadores de formato (email, URL, IBAN, UUID, semver…)"),
    # sec
    ("container-scan", "sec", ["trivy", "grype"], "CVEs en imágenes, filesystems y repos"),
    ("sbom-gen", "sec", ["syft"], "Generar SBOM (SPDX/CycloneDX) de imagen o proyecto"),
    ("image-sign", "sec", ["cosign"], "Firmar y verificar imágenes y artefactos"),
    ("iac-scan", "sec", ["checkov", "tfsec"], "Malas configuraciones en Terraform/K8s/Dockerfile"),
    ("secret-scan", "sec", ["gitleaks", "trufflehog"], "Secretos en el working tree y en el historial git"),
    ("dep-licenses", "sec", ["pip-licenses", "license-checker"], "Informe de licencias de dependencias con allowlist"),
    ("cve-lookup", "sec", ["curl"], "Detalles y severidad de un CVE/GHSA/OSV por id"),
    # bench
    ("bench-cmd", "bench", ["hyperfine"], "Benchmark estadístico de comandos con comparativa"),
    ("http-load", "bench", ["k6", "hey"], "Carga HTTP con umbrales de fallo y percentiles"),
    ("net-bench", "bench", ["iperf3"], "Ancho de banda y jitter entre hosts"),
    ("disk-bench", "bench", ["fio"], "IOPS y throughput de disco"),
    ("py-profile", "bench", ["py-spy"], "Perfilado de procesos Python en ejecución, sin reiniciar"),
    ("flamegraph", "bench", ["perf", "flamegraph"], "Flamegraphs de CPU de cualquier proceso"),
    # ── Ampliación v0.2 · categorías existentes ──────────────────────────
    # fs
    ("file-split", "fs", ["split", "cat"], "Trocear ficheros grandes y recomponerlos con verificación"),
    ("compare-dirs", "fs", ["diff", "rsync"], "Diff recursivo entre directorios con resumen por estado"),
    ("checksum-tree", "fs", ["sha256sum", "b3sum"], "Manifiesto de hashes de un árbol y verificación"),
    ("symlink-tool", "fs", ["ln", "find"], "Crear, resolver y auditar enlaces simbólicos rotos"),
    ("file-meta", "fs", ["stat"], "Metadatos completos de fichero (stat) en JSON"),
    ("shred-secure", "fs", ["shred"], "Borrado irrecuperable de ficheros sensibles"),
    ("temp-workspace", "fs", ["mktemp"], "Workspace temporal con limpieza automática al salir"),
    # text
    ("markdown-tool", "text", ["mdformat", "pandoc"], "TOC, numeración de headers y md a HTML"),
    ("frontmatter-tool", "text", ["python-frontmatter"], "Leer/editar frontmatter YAML (clave para SKILL.md)"),
    ("table-convert", "text", ["python", "miller"], "CSV/TSV a tabla Markdown alineada y viceversa"),
    ("jsonl-tool", "text", ["jq", "python"], "Split/sample/merge/validar NDJSON línea a línea"),
    ("slugify", "text", ["python"], "Normalizar cadenas a slugs seguros para rutas/URLs"),
    ("string-case", "text", ["python"], "Conversión camel/snake/kebab/title en lote"),
    ("sort-versions", "text", ["sort", "python"], "Ordenar listas de versiones con semántica semver"),
    ("ini-tool", "text", ["crudini"], "Leer/editar ficheros INI y .properties"),
    # docs
    ("diagram-render", "docs", ["mmdc", "plantuml", "d2", "dot"], "Mermaid/PlantUML/D2/Graphviz a SVG/PNG"),
    ("pdf-form-fill", "docs", ["pypdf", "pdftk"], "Rellenar formularios PDF desde JSON"),
    ("docx-template", "docs", ["docxtpl"], "Rellenar plantillas docx con variables y tablas"),
    ("markdown-slides", "docs", ["marp-cli"], "Markdown a presentación HTML/PPTX"),
    ("subtitle-tool", "docs", ["ffmpeg", "python"], "Extraer/convertir/desplazar subtítulos SRT/VTT"),
    ("video-info", "docs", ["ffprobe"], "Metadatos completos de medios en JSON"),
    ("audio-normalize", "docs", ["ffmpeg"], "Normalización de loudness EBU R128"),
    ("audio-concat", "docs", ["ffmpeg"], "Unir pistas de audio con crossfade y silencios"),
    ("qr-tool", "docs", ["qrencode", "zbar"], "Generar y leer códigos QR"),
    ("epub-tool", "docs", ["pandoc", "calibre"], "Crear/extraer/convertir EPUB"),
    # containers
    ("registry-tool", "containers", ["skopeo", "crane"], "Copiar imágenes entre registries, listar tags e inspeccionar manifests sin docker"),
    ("image-layers", "containers", ["dive"], "Analizar capas, tamaño y desperdicio de una imagen"),
    ("k8s-events", "containers", ["kubectl"], "Eventos del namespace ordenados y filtrados"),
    ("k8s-top", "containers", ["kubectl"], "Uso real de CPU/memoria de pods y nodos en JSON"),
    ("k8s-rbac-check", "containers", ["kubectl"], "auth can-i para un usuario/SA y quién puede hacer qué"),
    ("k8s-cp", "containers", ["kubectl"], "Copiar ficheros pod-local con verificación"),
    ("k8s-debug", "containers", ["kubectl"], "Contenedor efímero de depuración en un pod en marcha"),
    ("k8s-wait", "containers", ["kubectl"], "Esperar una condición de recurso con timeout"),
    ("k8s-secret-tool", "containers", ["kubectl"], "Crear secrets desde .env/ficheros y decodificarlos"),
    ("k8s-resources", "containers", ["kubectl", "jq"], "Informe requests/limits vs uso real por namespace"),
    ("k8s-drain", "containers", ["kubectl"], "Cordon/drain seguro de nodos con confirmación"),
    ("argocd-app", "containers", ["argocd"], "Sync, estado y diff de aplicaciones GitOps"),
    ("velero-backup", "containers", ["velero"], "Backup/restore de namespaces del clúster"),
    # web
    ("rss-fetch", "web", ["feedparser"], "Parsear feeds RSS/Atom a JSON con filtros de fecha"),
    ("sitemap-parse", "web", ["curl", "python"], "Extraer y filtrar URLs de un sitemap.xml"),
    ("link-check", "web", ["lychee", "curl"], "Detectar enlaces rotos en un sitio o documento"),
    ("robots-check", "web", ["python"], "Comprobar si una ruta es rastreable según robots.txt"),
    ("http-serve", "web", ["python"], "Servir un directorio local por HTTP (previews)"),
    ("api-mock", "web", ["prism"], "Mock server desde una spec OpenAPI"),
    ("wayback-fetch", "web", ["curl"], "Recuperar snapshots históricos de archive.org"),
    ("media-fetch", "web", ["yt-dlp"], "Descargar vídeo/audio de plataformas con metadatos"),
    # net
    ("curl-timing", "net", ["curl"], "Desglose DNS/TCP/TLS/TTFB de una petición"),
    ("ip-info", "net", ["curl"], "Geo, ASN y reverse DNS de una IP"),
    ("listen-report", "net", ["ss"], "Qué proceso escucha en qué puerto, en JSON"),
    ("net-scan", "net", ["nmap"], "Descubrir hosts y puertos en infraestructura propia"),
    ("packet-capture", "net", ["tcpdump"], "Captura acotada (duración/filtro) para diagnóstico"),
    ("tunnel-expose", "net", ["cloudflared", "tailscale"], "Exponer un puerto local a internet temporalmente"),
    ("mdns-discover", "net", ["avahi-browse"], "Descubrir servicios en la LAN"),
    # vcs
    ("git-worktree", "vcs", ["git"], "Árboles de trabajo paralelos (agentes concurrentes)"),
    ("git-bisect", "vcs", ["git"], "Búsqueda binaria de regresiones, automatizable con run"),
    ("git-tag", "vcs", ["git"], "Tags semver, firmados, con push controlado"),
    ("git-stash", "vcs", ["git"], "Guardar/aplicar/listar cambios temporales"),
    ("git-submodule", "vcs", ["git"], "Añadir/actualizar/sincronizar submódulos"),
    ("git-hooks", "vcs", ["pre-commit"], "Instalar y ejecutar hooks gestionados"),
    ("git-archive", "vcs", ["git"], "Exportar snapshot limpio (sin .git) a tar/zip"),
    ("monorepo-affected", "vcs", ["turbo", "nx", "git"], "Paquetes afectados por un diff para build selectivo"),
    # forges
    ("gh-gist", "forges", ["gh"], "Crear/listar/clonar gists"),
    ("gh-search", "forges", ["gh"], "Buscar código, issues y repos"),
    ("gh-secret", "forges", ["gh"], "Secrets y variables de Actions por repo/org"),
    ("gh-project", "forges", ["gh"], "Items y campos de Projects v2"),
    ("gh-artifact", "forges", ["gh"], "Descargar artefactos y logs de runs"),
    ("codeowners-check", "forges", ["python"], "Validar CODEOWNERS y cobertura de rutas"),
    # pkg
    ("go-build", "pkg", ["go"], "Compilar/test/instalar módulos Go"),
    ("jvm-build", "pkg", ["mvn", "gradle"], "Compilar/test proyectos Maven/Gradle"),
    ("php-composer", "pkg", ["composer"], "Dependencias PHP"),
    ("ruby-bundle", "pkg", ["bundler"], "Dependencias Ruby"),
    ("mise-runtimes", "pkg", ["mise", "asdf"], "Instalar/fijar versiones de runtimes por proyecto"),
    ("nix-shell", "pkg", ["nix"], "Entorno reproducible efímero con paquetes dados"),
    ("outdated-report", "pkg", ["npm", "pip", "cargo"], "Dependencias desactualizadas multi-ecosistema en JSON"),
    ("pkg-publish", "pkg", ["npm", "twine"], "Publicar a npm/PyPI con verificaciones previas"),
    # data
    ("usql-query", "data", ["usql"], "Cliente SQL universal (una interfaz, 20+ motores)"),
    ("db-migrate", "data", ["alembic", "flyway", "golang-migrate"], "Aplicar/revertir migraciones con estado"),
    ("db-schema-diff", "data", ["migra", "atlas"], "Comparar esquemas entre dos bases"),
    ("db-seed", "data", ["faker"], "Generar datos falsos coherentes para pruebas"),
    ("parquet-tool", "data", ["pyarrow", "duckdb"], "Inspeccionar/convertir Parquet y Arrow"),
    ("duckdb-sql", "data", ["duckdb"], "SQL analítico directo sobre CSV/Parquet/JSON"),
    ("xlsx-tool", "data", ["openpyxl"], "Leer/escribir/transformar Excel (hojas, rangos, fórmulas)"),
    ("influx-query", "data", ["influx"], "Consultas de series temporales"),
    # crypto
    ("sops-tool", "crypto", ["sops"], "Cifrar/descifrar ficheros de config con claves age/KMS"),
    ("age-encrypt", "crypto", ["age"], "Cifrado moderno de ficheros, simple y scriptable"),
    ("vault-secret", "crypto", ["vault"], "Leer/escribir secretos en HashiCorp Vault"),
    ("cert-make", "crypto", ["mkcert", "openssl"], "Certificados autofirmados y CA local de desarrollo"),
    ("ssh-key-tool", "crypto", ["ssh-keygen"], "Generar/convertir/fingerprint de claves SSH"),
    ("totp-gen", "crypto", ["oathtool"], "Códigos TOTP para automatizaciones con 2FA"),
    # proc
    ("date-calc", "proc", ["dateutils", "python"], "Sumar/restar fechas, diferencias y días laborables"),
    ("tz-convert", "proc", ["python"], "Convertir horas entre zonas horarias"),
    ("cron-explain", "proc", ["croniter"], "Validar expresiones cron y listar próximas ejecuciones"),
    ("sys-info", "proc", ["lshw", "inxi"], "Inventario de hardware y SO en JSON"),
    ("gpu-info", "proc", ["nvidia-smi"], "Estado y memoria de GPUs en JSON"),
    ("service-ctl", "proc", ["systemctl"], "Gestionar servicios systemd de forma scriptable"),
    ("journal-query", "proc", ["journalctl"], "Consultar journald con filtros en JSON"),
    ("term-record", "proc", ["asciinema"], "Grabar sesiones de terminal (auditoría de agentes)"),
    # quality
    ("lint-sh", "quality", ["shellcheck", "shfmt"], "Lint y formato de shell (los propios scripts del repo)"),
    ("lint-yaml", "quality", ["yamllint"], "Lint de YAML"),
    ("lint-docker", "quality", ["hadolint"], "Lint de Dockerfiles"),
    ("lint-md", "quality", ["markdownlint"], "Lint de Markdown"),
    ("cloc", "quality", ["tokei"], "Líneas de código por lenguaje en JSON"),
    ("complexity-report", "quality", ["radon", "lizard"], "Complejidad ciclomática y mantenibilidad"),
    ("dead-code", "quality", ["vulture", "knip"], "Código muerto en Python/JS"),
    ("todo-scan", "quality", ["ripgrep", "git"], "TODO/FIXME/HACK con contexto y autor en JSON"),
    ("codemod", "quality", ["ast-grep"], "Búsqueda y refactor estructural por patrones AST"),
    ("visual-diff", "quality", ["imagemagick"], "Comparar imágenes/screenshots con umbral"),
    ("a11y-check", "quality", ["pa11y", "axe"], "Auditoría de accesibilidad de una URL"),
    ("lighthouse-audit", "quality", ["lighthouse"], "Rendimiento/SEO/buenas prácticas web en JSON"),
    # api
    ("grpc-call", "api", ["grpcurl"], "Invocar servicios gRPC con reflexión"),
    ("websocket-client", "api", ["websocat"], "Conectar, enviar y escuchar WebSockets"),
    ("sse-client", "api", ["curl"], "Escuchar Server-Sent Events con filtros"),
    ("soap-call", "api", ["zeep"], "Servicios SOAP/WSDL legacy"),
    ("jsonrpc-call", "api", ["curl", "jq"], "Llamadas JSON-RPC 2.0"),
    ("api-diff", "api", ["oasdiff"], "Cambios incompatibles entre dos specs OpenAPI"),
    ("oauth-token", "api", ["curl"], "Tokens OAuth2 (client credentials, device) para Cognito/Keycloak"),
    ("stripe-tool", "api", ["stripe"], "Disparar eventos de prueba y reenviar webhooks"),
    # cloud (ampliación)
    ("coolify-api", "cloud", ["curl"], "Despliegues y servicios vía API de Coolify"),
    ("cloudflare-tool", "cloud", ["flarectl", "curl"], "DNS, purga de caché y reglas en Cloudflare"),
    ("hetzner-cli", "cloud", ["hcloud"], "Servidores, volúmenes y firewalls en Hetzner"),
    ("do-cli", "cloud", ["doctl"], "Recursos de DigitalOcean"),
    ("fly-deploy", "cloud", ["flyctl"], "Desplegar y escalar en Fly.io"),
    ("paas-deploy", "cloud", ["vercel", "netlify"], "Desplegar a Vercel/Netlify"),
    ("infracost", "cloud", ["infracost"], "Coste estimado de un plan de Terraform"),
    ("pulumi-run", "cloud", ["pulumi"], "IaC con Pulumi (up/preview/destroy)"),
    ("terragrunt-run", "cloud", ["terragrunt"], "Orquestar módulos Terraform multi-entorno"),
]

# Detalle adicional para los scripts ya implementados.
IMPLEMENTED: dict[str, dict] = {
    "find-files": {
        "lang": "bash",
        "flags": ["--name", "--ext", "--type", "--max-depth", "--newer-than", "--larger-than", "--json"],
        "usage": "find-files src --ext py --newer-than 7 --json",
    },
    "web-to-markdown": {
        "lang": "python",
        "runner": "uv run",
        "deps": ["trafilatura>=1.12,<3"],
        "flags": ["--json", "--include-links", "--timeout"],
        "usage": "uv run web/web-to-markdown <URL> --json",
        "notes": "Fallback de descarga con la confianza TLS del sistema: funciona tras proxies corporativos con inspección TLS",
    },
    "k8s-get": {
        "lang": "bash",
        "flags": ["--namespace", "--all-namespaces", "--selector", "--describe", "--wide", "--json"],
        "env": ["KUBECTL"],
        "notes": "Compatible con OpenShift usando KUBECTL=oc; sonda de conectividad vía /version (apta para RBAC restringido)",
        "usage": "KUBECTL=oc k8s-get pods -n NS -l app=api --json",
    },
    "gh-issue": {
        "lang": "bash",
        "subcommands": ["list", "view", "create", "comment", "close", "reopen"],
        "env": ["GH_TOKEN", "GITHUB_TOKEN"],
        "flags": ["--repo", "--json", "--dry-run", "--state", "--limit", "--label", "--title", "--body"],
        "notes": "--dry-run imprime el comando exacto y no requiere 'gh' ni token",
        "usage": "gh-issue list -R owner/repo -s open --json",
    },
    "json-schema-validate": {
        "lang": "python",
        "runner": "uv run",
        "deps": ["jsonschema>=4.21", "PyYAML>=6"],
        "flags": ["--schema", "--json"],
        "notes": "Valida JSON y YAML multi-documento; acepta '-' para stdin (salidas de agentes)",
        "usage": "uv run validate/json-schema-validate salida.json --schema esquema.yaml",
    },
    "llm-call": {
        "lang": "python",
        "runner": "python3",
        "deps": [],
        "env": ["LLM_BASE_URL", "LLM_MODEL", "LLM_API_KEY", "OPENAI_API_KEY", "ANTHROPIC_API_KEY"],
        "flags": ["--file", "--system", "--api", "--model", "--base-url", "--temperature",
                  "--max-tokens", "--timeout", "--retries", "--json"],
        "notes": "Solo stdlib (confianza TLS del sistema); OpenAI-compatible y Anthropic; reintentos ante 429/5xx",
        "usage": "echo 'hola' | llm-call --model gpt-4o --json",
    },
    "kestra-flow": {
        "lang": "bash",
        "subcommands": ["validate", "deploy", "execute", "status", "logs", "list"],
        "env": ["KESTRA_URL", "KESTRA_TENANT", "KESTRA_API_TOKEN", "KESTRA_USER", "KESTRA_PASSWORD"],
        "flags": ["--input", "--wait", "--wait-timeout", "--json", "--dry-run"],
        "notes": "API REST; --wait sigue la ejecución hasta estado terminal; --dry-run no requiere servidor",
        "usage": "kestra-flow execute prod etl --input fecha=2026-06-10 --wait",
    },
    "xlsx-tool": {
        "lang": "python",
        "runner": "uv run",
        "deps": ["openpyxl>=3.1"],
        "subcommands": ["info", "sheets", "csv", "json"],
        "flags": ["--sheet", "--no-header", "--json"],
        "notes": "--sheet por índice (1-based) o nombre; read-only y data_only",
        "usage": "uv run data/xlsx-tool csv brd.xlsx --sheet Requisitos",
    },
    "k8s-rbac-check": {
        "lang": "bash",
        "env": ["KUBECTL"],
        "flags": ["--list", "--namespace", "--all-namespaces", "--as", "--as-group",
                  "--sa", "--subresource", "--name", "--json"],
        "notes": "auth can-i; soporta varios verbos, impersonación de usuario/SA y --list; KUBECTL=oc para OpenShift",
        "usage": "k8s-rbac-check get,list,watch pods -n falcone --json",
    },
    "oauth-token": {
        "lang": "bash",
        "subcommands": ["client_credentials", "password", "refresh_token", "device"],
        "env": ["OAUTH_TOKEN_URL", "OAUTH_CLIENT_ID", "OAUTH_CLIENT_SECRET", "OAUTH_DEVICE_URL"],
        "flags": ["--token-url", "--client-id", "--client-secret", "--scope", "--audience",
                  "--username", "--password", "--refresh-token", "--device-url", "--auth-basic",
                  "--interval", "--device-timeout", "--timeout", "--json", "--dry-run"],
        "notes": "OAuth2 para Cognito/Keycloak/Auth0; imprime solo el access_token (componible); --dry-run enmascara secretos",
        "usage": "TOKEN=\"$(oauth-token client_credentials --scope api/read --auth-basic)\"",
    },
    "coolify-api": {
        "lang": "bash",
        "subcommands": ["apps", "app", "services", "databases", "deployments",
                        "deploy", "start", "stop", "restart"],
        "env": ["COOLIFY_URL", "COOLIFY_TOKEN"],
        "flags": ["--force", "--tag", "--json", "--dry-run"],
        "notes": "API v4 de Coolify; operaciones de escritura (deploy/start/stop/restart) con --dry-run sin servidor",
        "usage": "coolify-api deploy <uuid> --force",
    },
    "secret-scan": {
        "lang": "bash",
        "tools": ["gitleaks", "trufflehog"],
        "flags": ["--git-history", "--tool", "--only-verified", "--json", "--dry-run"],
        "notes": "Autodetecta gitleaks (preferido) o trufflehog; exit 1 si hay hallazgos (apto para CI); --dry-run sin la herramienta",
        "usage": "secret-scan . --git-history --json",
    },
    "container-scan": {
        "lang": "bash",
        "tools": ["trivy", "grype"],
        "flags": ["--fs", "--severity", "--tool", "--ignore-unfixed", "--json", "--dry-run"],
        "notes": "Autodetecta trivy (preferido) o grype; umbral de severidad; exit 1 si hay vulnerabilidades; --dry-run sin la herramienta",
        "usage": "container-scan registry.local/api:latest --severity CRITICAL,HIGH",
    },
}


def validate() -> None:
    """Falla con un mensaje claro si el catálogo es inconsistente."""
    errors: list[str] = []
    seen: set[str] = set()
    for sid, _, _, _ in SCRIPTS:
        if sid in seen:
            errors.append(f"id duplicado en SCRIPTS: {sid}")
        seen.add(sid)
    cat_ids = {c for c, _ in CATEGORIES}
    for sid, cat, _, _ in SCRIPTS:
        if cat not in cat_ids:
            errors.append(f"{sid}: categoría desconocida '{cat}'")
    root = Path(__file__).parent
    for sid in IMPLEMENTED:
        if sid not in seen:
            errors.append(f"IMPLEMENTED contiene un id que no está en SCRIPTS: {sid}")
            continue
        cat = next(c for s, c, _, _ in SCRIPTS if s == sid)
        if not (root / cat / sid).is_file():
            errors.append(f"{sid}: marcado 'implemented' pero falta el fichero {cat}/{sid}")
    if errors:
        raise SystemExit("[build_catalog] catálogo inconsistente:\n  - " + "\n  - ".join(errors))


def build() -> dict:
    validate()
    scripts = []
    for sid, cat, base, desc in SCRIPTS:
        entry = {
            "id": sid,
            "category": cat,
            "path": f"{cat}/{sid}",
            "base": base,
            "description": desc,
            "status": "implemented" if sid in IMPLEMENTED else "planned",
        }
        if sid in IMPLEMENTED:
            entry.update(IMPLEMENTED[sid])
        scripts.append(entry)

    return {
        "version": VERSION,
        "conventions": {
            "output": "datos por stdout, mensajes por stderr",
            "json": "flag --json para salida estructurada",
            "help": "--help funciona siempre, aunque falte la herramienta base",
            "order": "validar argumentos (exit 2) antes de comprobar dependencias (exit 127)",
            "python_deps": "dependencias en línea (PEP 723), ejecutar con `uv run`; import dentro de main()",
            "destructive": "flag --dry-run en operaciones que escriben/borran; no requiere credenciales",
            "exit_codes": "0 ok · 1 ejecución · 2 uso incorrecto · 127 falta la herramienta",
            "secrets": "credenciales desde variables de entorno, nunca hardcodeadas",
        },
        "categories": [{"id": cid, "name": name, "dir": f"{cid}/"} for cid, name in CATEGORIES],
        "scripts": scripts,
    }


def main() -> None:
    catalog = build()
    out = Path(__file__).parent / "catalog.json"
    out.write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    impl = sum(1 for s in catalog["scripts"] if s["status"] == "implemented")
    total = len(catalog["scripts"])
    print(f"catalog.json: {total} scripts en {len(catalog['categories'])} categorías ({impl} implementados).")


if __name__ == "__main__":
    main()
