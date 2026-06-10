<!-- Thanks for contributing! Please read CONTRIBUTING.md and SECURITY.md first. -->

## What does this PR do?

<!-- One or two sentences. Link the issue it closes, if any: "Closes #123". -->

## Type of change

- [ ] New script
- [ ] Fix / improvement to an existing script
- [ ] Docs (README / translations / guides)
- [ ] Repo tooling (catalog, templates, tests)
- [ ] CI / workflows (expect extra review — see SECURITY.md)

## Checklist

- [ ] I ran `bash tests/run_tests.sh` locally and it passes.
- [ ] I ran `python3 build_catalog.py` and the catalog is consistent.
- [ ] The script follows the conventions in CONTRIBUTING.md
      (stdout/stderr split, `--help` without dependencies, `--json`,
      `--dry-run` on write operations, exit-code contract, no hardcoded secrets).
- [ ] **The test suite stays hermetic**: my changes add NO network calls, NO real
      credentials, and NO `gh`/`kubectl`/cloud access to the tests.
- [ ] I did NOT add or modify anything under `.github/workflows/` (unless this PR
      is specifically about CI, in which case I explain why below).
- [ ] No remote-code execution patterns (`curl | bash`, fetching+running remote
      code, obfuscated or base64-encoded payloads).
- [ ] Any new third-party GitHub Action is pinned to a full commit SHA.

## Notes for reviewers

<!-- Anything that needs human attention: new external tools a script wraps,
     why a workflow change is necessary, etc. -->
