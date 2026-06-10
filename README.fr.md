# skillkit

[English](README.md) · [Español](README.es.md) · [中文](README.zh-CN.md) · [Deutsch](README.de.md) · **Français**

Une bibliothèque de **scripts réutilisables** que les Agent Skills peuvent appeler pour
agir sur leur bac à sable. Chaque script est un utilitaire en ligne de commande
autonome, destiné à être copié dans le dossier `scripts/` d'une skill ou référencé comme
dépendance partagée.

État : 13 scripts implémentés qui fixent le motif, plus des gabarits et un générateur
pour le répliquer, une suite de tests de fumée, et un index (`catalog.json`) comptant
**338 scripts répartis en 23 catégories** (le reste marqué `planned`, à implémenter par
lots).

## Structure

```
skillkit/
├── README.md              # anglais (par défaut) · aussi .es .zh-CN .de .fr
├── catalog.json           # index lisible par machine (généré par build_catalog.py)
├── build_catalog.py       # régénère et VALIDE catalog.json
├── new-script             # génère un nouveau script à partir d'un gabarit
├── templates/             # template.bash et template.py (le motif codifié)
├── tests/run_tests.sh     # tests de fumée du dépôt
├── fs/                    # fichiers et recherche         → find-files ✓
├── text/                  # texte et données structurées
├── docs/                  # conversion de documents et médias
├── containers/            # docker / k8s / openshift       → k8s-get, k8s-rbac-check ✓
├── web/                   # téléchargement et scraping     → web-to-markdown ✓
├── net/                   # réseau et diagnostic
├── vcs/                   # git / mercurial / svn
├── forges/                # github / gitlab / etc.         → gh-issue ✓
├── pkg/                   # paquets et dépendances
├── data/                  # bases de données et données    → xlsx-tool ✓
├── crypto/                # encodage / crypto / secrets
├── proc/                  # système, processus, orchestration locale
├── quality/               # tests, linting, qualité
├── api/                   # client HTTP/API générique      → oauth-token ✓
├── cloud/                 # clouds et infrastructure       → coolify-api ✓
├── ai/                    # IA et LLM                     → llm-call ✓
├── obs/                   # observabilité
├── msg/                   # messagerie et notifications
├── store/                 # stockage d'objets et sauvegardes
├── orch/                  # orchestrateurs de workflows    → kestra-flow ✓
├── validate/              # schémas et politiques          → json-schema-validate ✓
├── sec/                   # sécurité et chaîne d'approvisionnement → secret-scan, container-scan ✓
└── bench/                 # performance
```

## Conventions de conception

1. **Sortie** : les données vont vers `stdout` ; les messages et erreurs vers `stderr`.
2. **`--json`** : tout script renvoyant des données propose une sortie structurée.
3. **`--help` toujours** : fonctionne même si l'outil de base ou les dépendances
   manquent. En Python, les imports de dépendances sont pour cette raison dans `main()`.
4. **Ordre des vérifications** : valider les arguments (sortie 2) *avant* de vérifier
   les dépendances (sortie 127). Une erreur d'usage est signalée de la même façon avec
   ou sans l'outil.
5. **Dépendances en ligne** (Python) : PEP 723 + `uv run` ; sans installation préalable.
6. **`--dry-run`** sur toute opération qui écrit ou supprime : affiche la commande
   exacte et **ne requiert ni l'outil ni d'identifiants** (aperçu universel).
7. **Codes de sortie** : `0` ok · `1` erreur d'exécution · `2` usage incorrect ·
   `127` outil manquant (· `3` « aucun résultat » pour les extracteurs).
8. **Aucun secret en dur** : identifiants et jetons proviennent de variables
   d'environnement.
9. **Une responsabilité par script** : bien faire une chose et composer.

## Scripts implémentés

**`fs/find-files`** — chercher des fichiers par nom, type, extension, date ou taille.
```bash
find-files src --ext py --newer-than 7
find-files . --type d --name 'test*' --json
```

**`web/web-to-markdown`** — télécharger une URL et extraire son contenu principal en
Markdown. PEP 723 (nécessite `uv`) ; `--timeout` configurable. Si le téléchargement
direct échoue, il réessaie avec le magasin de confiance TLS du système et les proxys
d'environnement, ce qui le rend opérationnel derrière des proxys d'entreprise à
inspection TLS (Fortinet, Zscaler…).
```bash
uv run web/web-to-markdown https://example.com/post --json --timeout 20
```

**`containers/k8s-get`** — lister ou décrire des ressources Kubernetes/OpenShift.
La sonde de connectivité utilise `/version` (lisible par tout utilisateur authentifié),
ce qui la rend opérationnelle sur des clusters au RBAC restreint où `cluster-info`
échouerait.
```bash
k8s-get pods -n falcone -l app=api --wide
KUBECTL=oc k8s-get deployment api -n falcone --json
```

**`forges/gh-issue`** — gérer les issues GitHub. Jeton via `GH_TOKEN`/`GITHUB_TOKEN` ;
`--dry-run` affiche la commande exacte sans nécessiter `gh` ni jeton.
```bash
gh-issue list -R my-org/falcone -s open -l tenant-isolation --json
gh-issue create -R my-org/falcone -t "Fuite inter-locataires" -b "Détails…" --dry-run
```

**`validate/json-schema-validate`** — valider du JSON/YAML (multi-documents) contre un
JSON Schema. Conçu pour vérifier les sorties structurées d'agents avant utilisation ;
accepte `-` pour lire depuis stdin. PEP 723 (nécessite `uv`).
```bash
uv run validate/json-schema-validate ard.json --schema schemas/ard.schema.yaml
kestra-flow logs $EXEC | uv run validate/json-schema-validate - --schema out.json
```

**`ai/llm-call`** — appeler un point d'accès LLM et renvoyer la réponse. Bibliothèque
standard uniquement (aucune installation), confiance TLS du système, dialectes
compatibles OpenAI et Anthropic, réessais sur 429/5xx. Fonctionne aussi bien pour des
points d'accès privés (vLLM, Ollama, LiteLLM) que pour les API publiques. Configuré via
`LLM_BASE_URL`/`LLM_MODEL`/`LLM_API_KEY`.
```bash
echo "Résume ce BRD" | llm-call --system "Tu es un architecte" --model qwen2 \
    --base-url http://vllm.internal:8000/v1 --json
```

**`orch/kestra-flow`** — valider, déployer et exécuter des flux Kestra via l'API REST.
`--wait` suit l'exécution jusqu'à son état terminal ; `--dry-run` montre l'appel sans
serveur. Authentification par jeton (EE/Cloud) ou identifiant/mot de passe (OSS).
```bash
kestra-flow validate flows/ard-pipeline.yaml
kestra-flow execute prod brd-to-ard --input brd=s3://bucket/brd.xlsx --wait
```

**`data/xlsx-tool`** — inspecter et convertir Excel (`info`/`sheets`/`csv`/`json`).
`--sheet` par index (à partir de 1) ou par nom. Utile pour ingérer les BRD Excel du
pipeline ARD. PEP 723 (nécessite `uv`).
```bash
uv run data/xlsx-tool info brd.xlsx --json
uv run data/xlsx-tool json brd.xlsx --sheet Requirements
```

**`containers/k8s-rbac-check`** — auditer les permissions RBAC (`auth can-i`) sur
Kubernetes/OpenShift. Prend en charge plusieurs verbes, l'usurpation d'utilisateur ou de
ServiceAccount, et `--list`. En lecture seule. `KUBECTL=oc` pour OpenShift.
```bash
k8s-rbac-check get,list,watch pods -n falcone --json
k8s-rbac-check delete secrets -n other-tenant --sa falcone:api   # isolation ok ?
```

**`api/oauth-token`** — obtenir un jeton OAuth2 et l'afficher (composable). Grants
`client_credentials`, `password`, `refresh_token` et `device` (flux d'appareil avec
sondage). Pour Cognito, Keycloak, Auth0… `--auth-basic` envoie les identifiants en
en-tête Basic ; `--dry-run` montre la requête avec le secret masqué.
```bash
TOKEN="$(oauth-token client_credentials --scope 'api/read' --auth-basic)"
oauth-token device --scope 'openid profile' --json
```

**`cloud/coolify-api`** — piloter Coolify via son API v4 : lister applications, services
et bases de données, et déclencher `deploy`/`start`/`stop`/`restart`. Les opérations
d'écriture prennent en charge `--dry-run` sans serveur. Configuré via
`COOLIFY_URL`/`COOLIFY_TOKEN`.
```bash
coolify-api apps --json
coolify-api deploy 9b7c... --force
```

**`sec/secret-scan`** — chercher des secrets exposés avec gitleaks (préféré) ou
trufflehog, en détectant automatiquement l'outil. Arbre de travail par défaut, ou
`--git-history` pour tout l'historique. Renvoie la sortie 1 en cas de trouvailles
(adapté à la CI).
```bash
secret-scan . --git-history --json
secret-scan src --tool trufflehog --only-verified
```

**`sec/container-scan`** — chercher des CVE dans des images ou via `--fs` avec trivy
(préféré) ou grype, en détectant automatiquement l'outil. Seuil via `--severity` ;
sortie 1 si des vulnérabilités du niveau indiqué sont trouvées.
```bash
container-scan registry.local/falcone-api:latest --severity CRITICAL,HIGH
container-scan --fs . --ignore-unfixed --json
```

## Tests

```bash
bash tests/run_tests.sh
```

Vérifie la syntaxe, l'aide sans dépendances, les erreurs d'usage (sortie 2), le
comportement fonctionnel (recherche avec `--json`, `--dry-run` sans identifiants,
génération depuis un gabarit) et la cohérence du catalogue. Il ne nécessite ni `gh` ni
`kubectl` : il vérifie justement que les scripts se dégradent proprement en leur
absence.

## Ajouter un script

```bash
./new-script text json-query bash -d "Interroger/transformer du JSON" -b jq
```

1. Implémenter la logique dans la section 3 du gabarit généré.
2. Ajouter l'entrée dans `SCRIPTS` de `build_catalog.py` (et dans `IMPLEMENTED` une fois
   terminé).
3. Régénérer l'index : `python3 build_catalog.py` (valide ids, catégories et fichiers).
4. Lancer la suite : `bash tests/run_tests.sh`.

## Comment une skill l'utilise

Dans le `SKILL.md`, pointez vers le script et décrivez quand l'utiliser ; le code reste
hors du contexte (divulgation progressive) :

```markdown
## Convertir une page web en Markdown
Quand vous avez besoin du contenu épuré d'une URL, exécutez :

    uv run scripts/web-to-markdown <URL> --json

Renvoie un objet JSON avec `title`, `author`, `date` et `markdown`.
```

Deux façons d'intégrer la bibliothèque :
- **Copier** le script isolé dans le `scripts/` de la skill (autonome).
- **Référencer** ce dépôt comme dépendance partagée (p. ex. un sous-module git).

## Index complet

`catalog.json` répertorie les 338 scripts avec catégorie, outils de base, statut et —
pour ceux qui sont implémentés — options, exemple d'usage et notes. `build_catalog.py`
le régénère et **échoue avec un message clair** en cas d'ids en double, de catégories
invalides ou de scripts marqués implémentés mais absents du disque.

## Notes

- Après décompression, si le bit d'exécution n'est pas conservé : `chmod +x <script>`.
- Les scripts Python à en-tête PEP 723 nécessitent `uv` (https://docs.astral.sh/uv/).
- `KUBECTL=oc` réutilise les scripts de `containers/` sur OpenShift.
- Avant de publier le dépôt, ajoutez une licence (Apache-2.0 ou MIT conviennent bien à
  l'écosystème des skills).
