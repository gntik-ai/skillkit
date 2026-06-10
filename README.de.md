# skillkit

[English](README.md) · [Español](README.es.md) · [中文](README.zh-CN.md) · **Deutsch** · [Français](README.fr.md)

Eine Bibliothek **wiederverwendbarer Skripte**, die Agent Skills aufrufen können, um auf
ihre Sandbox einzuwirken. Jedes Skript ist ein eigenständiges Kommandozeilen-Werkzeug,
gedacht zum Kopieren in den `scripts/`-Ordner einer beliebigen Skill oder zur
Einbindung als gemeinsame Abhängigkeit.

Status: 13 implementierte Skripte, die das Muster festlegen, dazu Vorlagen und ein
Generator zum Replizieren, eine Smoke-Test-Suite sowie ein Index (`catalog.json`) mit
**338 Skripten in 23 Kategorien** (der Rest als `planned` markiert, in Schüben
umsetzbar).

## Struktur

```
skillkit/
├── README.md              # Englisch (Standard) · auch .es .zh-CN .de .fr
├── catalog.json           # maschinenlesbarer Index (von build_catalog.py erzeugt)
├── build_catalog.py       # erzeugt und VALIDIERT catalog.json
├── new-script             # erstellt ein neues Skript aus einer Vorlage
├── templates/             # template.bash und template.py (das kodifizierte Muster)
├── tests/run_tests.sh     # Smoke-Tests des Repositorys
├── fs/                    # Dateien und Suche             → find-files ✓
├── text/                  # Text und strukturierte Daten
├── docs/                  # Dokument- und Medienkonvertierung
├── containers/            # docker / k8s / openshift       → k8s-get, k8s-rbac-check ✓
├── web/                   # Download und Scraping          → web-to-markdown ✓
├── net/                   # Netzwerk und Diagnose
├── vcs/                   # git / mercurial / svn
├── forges/                # github / gitlab / usw.         → gh-issue ✓
├── pkg/                   # Pakete und Abhängigkeiten
├── data/                  # Datenbanken und Daten          → xlsx-tool ✓
├── crypto/                # Kodierung / Krypto / Secrets
├── proc/                  # System, Prozesse, lokale Orchestrierung
├── quality/               # Tests, Linting, Qualität
├── api/                   # generischer HTTP/API-Client    → oauth-token ✓
├── cloud/                 # Clouds und Infrastruktur       → coolify-api ✓
├── ai/                    # KI und LLMs                   → llm-call ✓
├── obs/                   # Observability
├── msg/                   # Messaging und Benachrichtigungen
├── store/                 # Objektspeicher und Backups
├── orch/                  # Workflow-Orchestratoren        → kestra-flow ✓
├── validate/              # Schemata und Policies          → json-schema-validate ✓
├── sec/                   # Sicherheit und Lieferkette     → secret-scan, container-scan ✓
└── bench/                 # Performance
```

## Designkonventionen

1. **Ausgabe**: Daten gehen nach `stdout`; Meldungen und Fehler nach `stderr`.
2. **`--json`**: Jedes Skript, das Daten zurückgibt, bietet strukturierte Ausgabe.
3. **`--help` immer**: funktioniert auch ohne das Basiswerkzeug oder die Abhängigkeiten.
   In Python liegen die Importe der Abhängigkeiten deshalb innerhalb von `main()`.
4. **Prüfreihenfolge**: Argumente validieren (Exit 2) *vor* der Prüfung der
   Abhängigkeiten (Exit 127). Ein Nutzungsfehler wird mit oder ohne Werkzeug gleich
   gemeldet.
5. **Inline-Abhängigkeiten** (Python): PEP 723 + `uv run`; ohne vorherige Installation.
6. **`--dry-run`** bei jeder schreibenden oder löschenden Operation: gibt den exakten
   Befehl aus und **benötigt weder das Werkzeug noch Anmeldedaten** (universelle
   Vorschau).
7. **Exit-Codes**: `0` OK · `1` Laufzeitfehler · `2` falsche Nutzung ·
   `127` Werkzeug fehlt (· `3` „keine Ergebnisse“ bei Extraktoren).
8. **Keine hartkodierten Secrets**: Anmeldedaten und Tokens kommen aus
   Umgebungsvariablen.
9. **Eine Verantwortung pro Skript**: eine Sache gut machen und kombinieren.

## Implementierte Skripte

**`fs/find-files`** – Dateien nach Name, Typ, Endung, Datum oder Größe finden.
```bash
find-files src --ext py --newer-than 7
find-files . --type d --name 'test*' --json
```

**`web/web-to-markdown`** – eine URL herunterladen und ihren Hauptinhalt als Markdown
extrahieren. PEP 723 (benötigt `uv`); `--timeout` konfigurierbar. Schlägt der direkte
Download fehl, wird mit dem TLS-Truststore des Systems und den Umgebungs-Proxys erneut
versucht – so funktioniert es hinter Unternehmens-Proxys mit TLS-Inspektion (Fortinet,
Zscaler …).
```bash
uv run web/web-to-markdown https://example.com/post --json --timeout 20
```

**`containers/k8s-get`** – Kubernetes/OpenShift-Ressourcen auflisten oder beschreiben.
Die Verbindungsprüfung nutzt `/version` (für jeden authentifizierten Nutzer lesbar) und
funktioniert daher in Clustern mit eingeschränktem RBAC, wo `cluster-info` scheitern
würde.
```bash
k8s-get pods -n falcone -l app=api --wide
KUBECTL=oc k8s-get deployment api -n falcone --json
```

**`forges/gh-issue`** – GitHub-Issues verwalten. Token aus `GH_TOKEN`/`GITHUB_TOKEN`;
`--dry-run` gibt den exakten Befehl aus, ohne `gh` oder ein Token zu benötigen.
```bash
gh-issue list -R my-org/falcone -s open -l tenant-isolation --json
gh-issue create -R my-org/falcone -t "Mandantenübergreifendes Leck" -b "Details…" --dry-run
```

**`validate/json-schema-validate`** – JSON/YAML (mehrere Dokumente) gegen ein
JSON Schema validieren. Gedacht zur Prüfung strukturierter Agenten-Ausgaben vor ihrer
Verwendung; akzeptiert `-` zum Lesen von stdin. PEP 723 (benötigt `uv`).
```bash
uv run validate/json-schema-validate ard.json --schema schemas/ard.schema.yaml
kestra-flow logs $EXEC | uv run validate/json-schema-validate - --schema out.json
```

**`ai/llm-call`** – einen LLM-Endpunkt aufrufen und die Antwort zurückgeben. Nur
Standardbibliothek (keine Installation), TLS-Vertrauen des Systems, OpenAI-kompatibler
und Anthropic-Dialekt, Wiederholungen bei 429/5xx. Funktioniert für private Endpunkte
(vLLM, Ollama, LiteLLM) ebenso wie für öffentliche APIs. Konfiguriert über
`LLM_BASE_URL`/`LLM_MODEL`/`LLM_API_KEY`.
```bash
echo "Fasse dieses BRD zusammen" | llm-call --system "Du bist Architekt" --model qwen2 \
    --base-url http://vllm.internal:8000/v1 --json
```

**`orch/kestra-flow`** – Kestra-Flows über die REST-API validieren, bereitstellen und
ausführen. `--wait` verfolgt die Ausführung bis zum Endzustand; `--dry-run` zeigt den
Aufruf ohne Server. Authentifizierung per Token (EE/Cloud) oder Benutzer/Passwort
(OSS).
```bash
kestra-flow validate flows/ard-pipeline.yaml
kestra-flow execute prod brd-to-ard --input brd=s3://bucket/brd.xlsx --wait
```

**`data/xlsx-tool`** – Excel inspizieren und konvertieren (`info`/`sheets`/`csv`/`json`).
`--sheet` per 1-basiertem Index oder Name. Nützlich zum Einlesen der Excel-BRDs der
ARD-Pipeline. PEP 723 (benötigt `uv`).
```bash
uv run data/xlsx-tool info brd.xlsx --json
uv run data/xlsx-tool json brd.xlsx --sheet Requirements
```

**`containers/k8s-rbac-check`** – RBAC-Berechtigungen (`auth can-i`) auf
Kubernetes/OpenShift prüfen. Unterstützt mehrere Verben, Impersonation von Nutzer oder
ServiceAccount sowie `--list`. Nur lesend. `KUBECTL=oc` für OpenShift.
```bash
k8s-rbac-check get,list,watch pods -n falcone --json
k8s-rbac-check delete secrets -n other-tenant --sa falcone:api   # Isolation ok?
```

**`api/oauth-token`** – ein OAuth2-Token beziehen und ausgeben (kombinierbar). Grants
`client_credentials`, `password`, `refresh_token` und `device` (Device-Flow mit
Polling). Für Cognito, Keycloak, Auth0 … `--auth-basic` sendet die Anmeldedaten als
Basic-Header; `--dry-run` zeigt die Anfrage mit maskiertem Secret.
```bash
TOKEN="$(oauth-token client_credentials --scope 'api/read' --auth-basic)"
oauth-token device --scope 'openid profile' --json
```

**`cloud/coolify-api`** – Coolify über seine v4-API bedienen: Anwendungen, Dienste und
Datenbanken auflisten sowie `deploy`/`start`/`stop`/`restart` auslösen. Schreibende
Operationen unterstützen `--dry-run` ohne Server. Konfiguriert über
`COOLIFY_URL`/`COOLIFY_TOKEN`.
```bash
coolify-api apps --json
coolify-api deploy 9b7c... --force
```

**`sec/secret-scan`** – mit gitleaks (bevorzugt) oder trufflehog nach geleakten Secrets
suchen, mit automatischer Werkzeugerkennung. Standardmäßig der Arbeitsbaum, oder
`--git-history` für die vollständige Historie. Liefert Exit 1 bei Funden (CI-tauglich).
```bash
secret-scan . --git-history --json
secret-scan src --tool trufflehog --only-verified
```

**`sec/container-scan`** – mit trivy (bevorzugt) oder grype nach CVEs in Images oder
`--fs` suchen, mit automatischer Werkzeugerkennung. Schwelle per `--severity`; Exit 1,
wenn Schwachstellen der angegebenen Stufe gefunden werden.
```bash
container-scan registry.local/falcone-api:latest --severity CRITICAL,HIGH
container-scan --fs . --ignore-unfixed --json
```

## Tests

```bash
bash tests/run_tests.sh
```

Prüft Syntax, Hilfe ohne Abhängigkeiten, Nutzungsfehler (Exit 2), funktionales
Verhalten (Suche mit `--json`, `--dry-run` ohne Anmeldedaten, Erzeugung aus einer
Vorlage) und die Konsistenz des Katalogs. Es benötigt weder `gh` noch `kubectl`: Es
prüft gerade, dass die Skripte ohne diese Werkzeuge sauber abbauen.

## Ein Skript hinzufügen

```bash
./new-script text json-query bash -d "JSON abfragen/transformieren" -b jq
```

1. Die Logik in Abschnitt 3 der erzeugten Vorlage implementieren.
2. Den Eintrag in `SCRIPTS` in `build_catalog.py` ergänzen (und nach Fertigstellung in
   `IMPLEMENTED`).
3. Den Index neu erzeugen: `python3 build_catalog.py` (validiert IDs, Kategorien,
   Dateien).
4. Die Suite ausführen: `bash tests/run_tests.sh`.

## Wie eine Skill es nutzt

Verweise in der `SKILL.md` auf das Skript und beschreibe, wann es zu verwenden ist; der
Code bleibt außerhalb des Kontexts (Progressive Disclosure):

```markdown
## Eine Webseite in Markdown umwandeln
Wenn du den bereinigten Inhalt einer URL brauchst, führe aus:

    uv run scripts/web-to-markdown <URL> --json

Gibt ein JSON-Objekt mit `title`, `author`, `date` und `markdown` zurück.
```

Zwei Wege, die Bibliothek einzubinden:
- Das einzelne Skript in das `scripts/` der Skill **kopieren** (eigenständig).
- Dieses Repo als gemeinsame Abhängigkeit **referenzieren** (z. B. als git submodule).

## Vollständiger Index

`catalog.json` listet alle 338 Skripte mit Kategorie, Basiswerkzeugen, Status und – bei
den implementierten – Flags, einem Nutzungsbeispiel und Notizen. `build_catalog.py`
erzeugt ihn neu und **schlägt mit einer klaren Meldung fehl**, wenn es doppelte IDs,
ungültige Kategorien oder als implementiert markierte Skripte gibt, die nicht auf der
Platte existieren.

## Hinweise

- Falls das Ausführungs-Bit nach dem Entpacken fehlt: `chmod +x <script>`.
- Python-Skripte mit PEP-723-Kopf benötigen `uv` (https://docs.astral.sh/uv/).
- `KUBECTL=oc` nutzt die Skripte in `containers/` auf OpenShift wieder.
- Vor der Veröffentlichung des Repositorys eine Lizenz hinzufügen (Apache-2.0 oder MIT
  passen gut zum Skills-Ökosystem).
