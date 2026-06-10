# Contributing to skillkit

Thanks for your interest! This repo is a library of small, self-contained CLI scripts
that Agent Skills can call. Contributions that add a useful script, fix a bug, or
improve the docs are welcome.

Before anything else, please read **[SECURITY.md](SECURITY.md)** — it defines the
rules for forks and pull requests. The most important one: **fork PRs do not run CI
until a maintainer reviews the diff and approves the run.** This is intentional and
protects the project's CI runners from untrusted code.

## Ground rules (the short version)

- Keep the test suite **hermetic**: no network, no real credentials, no
  `gh`/`kubectl`/cloud calls in tests. Use `--dry-run`, `--help`, and local fixtures.
- Don't modify `.github/workflows/**` in a feature PR. Workflow changes go in a
  dedicated, clearly explained PR.
- No remote-code-execution patterns anywhere: no `curl | bash`, no downloading and
  executing remote code, no obfuscated/base64 payloads.
- Secrets come from environment variables only — never hardcoded, never printed.
- Pin any new third-party GitHub Action to a full commit SHA.

## Design conventions

Every script follows the same contract (this is what makes them composable and safe to
call from a skill):

1. **Output**: data to `stdout`; messages and errors to `stderr`.
2. **`--json`**: any script that returns data offers structured output.
3. **`--help` always works** — even when the base tool or dependencies are missing. In
   Python, import dependencies *inside* `main()` so `--help` never needs them.
4. **Check order**: validate arguments (exit `2`) **before** checking for the tool
   (exit `127`). A usage error must be reported the same way with or without the tool.
5. **Inline dependencies (Python)**: PEP 723 header + run via `uv run`; no prior install.
6. **`--dry-run`** on every operation that writes or deletes: print the exact command
   and require **neither the tool nor credentials**. Mask secrets in the output.
7. **Exit codes**: `0` ok · `1` runtime error · `2` incorrect usage · `127` missing
   tool · (`3` "no results" for extractors).
8. **No hardcoded secrets**: credentials/tokens from environment variables.
9. **One responsibility per script**: do one thing well; kebab-case names.

The templates in `templates/` encode this pattern. The implemented scripts (e.g.
`api/oauth-token`, `orch/kestra-flow`) are good references.

## Adding a script

1. **Check the catalog.** It may already be listed in `catalog.json` as `planned`.
2. **Scaffold it** from the template:
   ```bash
   ./new-script <category> <name> <bash|python> -d "One-line description" -b <base-tool>
   ```
3. **Implement** the logic in section 3 of the generated file. Follow the conventions
   above. Keep `--help`, usage validation, and `--dry-run` working without the tool.
4. **Register it** in `build_catalog.py`: add the entry to `SCRIPTS`, and once it's
   done, add a detailed entry to `IMPLEMENTED`.
5. **Regenerate and validate the catalog**:
   ```bash
   python3 build_catalog.py
   ```
   This fails loudly on duplicate ids, invalid categories, or implemented scripts that
   don't exist on disk.
6. **Run the suite** and make sure it passes:
   ```bash
   bash tests/run_tests.sh
   ```
   Add tests for your script in the same style: syntax, `--help` without dependencies,
   usage errors (exit 2), and a functional `--dry-run` check where applicable.
7. **Make it executable** in your commit: `chmod +x <category>/<name>`.

## Commit and PR hygiene

- One logical change per PR. Small PRs get reviewed faster.
- Reference the issue you're closing (`Closes #123`).
- Fill in the pull request template — the checklist mirrors the rules above.
- Run `bash tests/run_tests.sh` and `python3 build_catalog.py` locally before pushing.
- For shell scripts, `shellcheck` and `bash -n` should be clean; for Python,
  `python3 -m py_compile` should pass. CI runs all of these.

## Code of conduct

Be respectful and constructive. Harassment or abuse isn't tolerated. Maintainers may
edit, lock, or remove contributions and may decline any change without obligation.

## License

By contributing, you agree that your contributions are licensed under the
**Apache License 2.0** (see [LICENSE](LICENSE)), consistent with Section 5 of that
license.
