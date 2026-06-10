# Security Policy

This repository ships **executable scripts**. The main risk for an open project
like this is not the scripts you run on your own machine — it is **untrusted code
running in CI** when someone forks the repo and opens a pull request. This document
defines precise rules to keep that from happening, and explains *why* they work.

If you only read one thing: **fork pull requests never run CI automatically. A
maintainer reads the diff and approves the run first.** Everything else is
defense-in-depth around that single gate.

---

## Reporting a vulnerability

Do **not** open a public issue for a security problem. Use GitHub's private
reporting: repo **Security** tab → **Report a vulnerability** (Privately reported
vulnerabilities must be enabled in Settings → Code security). We aim to acknowledge
within a few business days. Please include a minimal reproduction and avoid sharing
secrets or real hostnames.

---

## Threat model: untrusted code in GitHub Actions

When a fork opens a PR, the workflow could try to execute attacker-controlled code
on GitHub's runners — to mine cryptocurrency, use the runner as an outbound proxy,
exfiltrate anything the runner can reach, or steal the repo token/secrets. We block
this in layers.

### 1. `pull_request`, never `pull_request_target`

The CI workflow triggers on `pull_request`. For PRs **from forks** this means:

- the `GITHUB_TOKEN` is **read-only**, and
- **no repository or organization secrets are exposed** to the job.

So even if malicious code executes, it **cannot push to the repository, cannot read
secrets, and cannot publish packages or releases**. The blast radius is limited to
"some compute ran on an ephemeral runner."

`pull_request_target` is the opposite — it runs with a **read-write token and access
to secrets**. It is **forbidden** in this repo for anything that checks out or runs
PR code. Do not introduce it.

### 2. A human approves before any fork PR runs

Required repository setting (maintainers, see the checklist below):

> Settings → Actions → General → *Fork pull request workflows from outside
> collaborators* → **Require approval for all outside collaborators.**

Do **not** use the looser "Require approval for first-time contributors only": a
contributor whose first trivial PR was merged could make a later malicious one run
without review. With "all outside collaborators", **every** fork PR run is gated on a
maintainer who has read the diff.

### 3. Least-privilege token and no ambient secrets

- The workflow sets `permissions: contents: read` at the top level. The token can
  only read the checkout — nothing else — even on `push` to `main`.
- `actions/checkout` uses `persist-credentials: false`, so the token is **not written
  to `.git/config`** where a script in the suite could read and reuse it.
- **No secrets are referenced anywhere in CI.** The test suite is hermetic by design
  (see rule 5). If a workflow ever genuinely needs a secret, it must run **only** on
  `push` to the main repo or via `workflow_dispatch` — **never** on `pull_request`,
  and it must live in a separate workflow file from the PR checks.

### 4. Bounded and pinned

- Every job sets `timeout-minutes`, and `concurrency` cancels superseded runs — a
  spam PR cannot tie up runners indefinitely or mine for hours.
- Third-party Actions must be pinned to a **full commit SHA** (not a tag — tags can be
  moved by an attacker). GitHub-owned `actions/*` may use a major tag (`@v4`) and are
  kept current by Dependabot.

### 5. The test suite stays hermetic

`tests/run_tests.sh` deliberately needs **no network, no credentials, and no
`gh`/`kubectl`/cloud access**. It exercises scripts through `--help`, usage-error
paths, `--dry-run` (which never contacts a server), and local fixtures. This keeps CI
from being a useful proxy or exfiltration vector and keeps runs reproducible. PRs that
make the tests reach the network or require secrets **will be rejected**.

### Residual risk we accept

The `suite` job does execute repo code (the harness, `build_catalog.py`, and a couple
of `uv` runs). That is unavoidable when testing a scripts repo. It is contained by the
human approval gate (rule 2) plus the read-only/no-secrets posture (rules 1, 3). The
static-analysis job, by contrast, only *parses* code (`shellcheck`, `bash -n`,
`py_compile`) and executes nothing.

---

## Rules for forks and pull requests

**Contributors must:**

1. Accept that **fork PRs do not run CI until a maintainer approves the run.** This is
   intentional; please be patient.
2. Keep the test suite hermetic — **no network, no real credentials, no
   `gh`/`kubectl`/cloud calls** added to tests. Use `--dry-run`, `--help`, and local
   fixtures.
3. **Not touch `.github/workflows/**`** in a feature PR. Workflow changes belong in a
   dedicated PR, clearly explained, and receive the highest scrutiny.
4. Avoid remote-code-execution patterns anywhere (scripts or tests): no `curl | bash`,
   no downloading-then-executing remote code, no obfuscated or base64-encoded payloads,
   no calling out to pastebins or shorteners.
5. Pin any new third-party GitHub Action to a full commit SHA.
6. Read secrets/config only from environment variables — never hardcode them, never
   print them (mask them, as the implemented scripts do in `--dry-run`).

**Maintainers must, before clicking "Approve and run" on a fork PR:**

1. Read the **entire** diff. Pay special attention to changes in `.github/workflows/**`,
   `tests/`, `build_catalog.py`, `new-script`, and any `*.bash`/`*.py` script.
2. Reject anything that adds network/secret use to CI, introduces
   `pull_request_target`, or contains the RCE patterns above.
3. Never approve a run you have not understood. If in doubt, ask the author to explain
   or to split the PR.

---

## Repository settings checklist (maintainers)

These are GitHub settings, not files in the repo. Configure them once:

- **Actions → General**
  - Fork PR workflows from outside collaborators → **Require approval for all outside
    collaborators.**
  - Workflow permissions → **Read repository contents and packages permissions**
    (read-only default token).
  - **Uncheck** "Allow GitHub Actions to create and approve pull requests."
- **Branches → Branch protection rule for `main`**
  - Require a pull request before merging; require **1+ approving review**.
  - Require review from **Code Owners** (uses `.github/CODEOWNERS`).
  - Require status checks to pass: select the **CI** checks (`static`, `suite`).
  - Require branches to be up to date; require conversation resolution.
  - Require linear history; **disallow force pushes and deletions**.
  - Include administrators.
- **Code security**
  - Enable **Private vulnerability reporting**.
  - Enable **Dependabot alerts** and **security updates**.
  - Enable **Secret scanning** and **push protection**.

---

## Optional hardening: egress control on the runner

To directly limit what a runner can do on the network (the cryptomining/proxy concern),
add [`step-security/harden-runner`](https://github.com/step-security/harden-runner) as
the **first** step of each job. Start in `audit` mode to learn the needed egress, then
switch to `block` with an allowlist. Pin it to a commit SHA per rule 5, e.g.:

```yaml
- name: Harden runner
  uses: step-security/harden-runner@<commit-sha>  # pin to a release SHA
  with:
    egress-policy: audit   # then: block, with allowed-endpoints
```

It is left out of the default workflow to keep the executable third-party surface at
zero; enable it once you have verified the SHA.

---

## Supported versions

This project is distributed as source scripts with no released binaries; security
fixes are applied to the `main` branch.
