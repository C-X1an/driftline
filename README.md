# Driftline

An experimental Python CLI that compares a project's stated intent in `vision.md` with a model of its code structure. It combines Python AST extraction with local language-model reasoning, then proposes a diff for human review.

**Status:** prototype. Model suggestions are fallible; an “aligned” result is not proof that software implements a guarantee. The bundled cloud adapter is development code, and the CLI currently selects the local/free path.

## Install

Python 3.10+ is declared; Python 3.12 is the tested reference environment. Install this checkout in a virtual environment:

```sh
python -m venv .venv
# macOS/Linux: source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m pip install --no-deps .
driftline --help
```

The package includes nested modules and all six prompt templates. `requirements.in` and package metadata list the three direct dependencies; `requirements.txt` pins resolved runtime dependencies for the reference environment.

## Workflow

Run these commands in the Git repository you want to inspect:

```sh
driftline init
driftline clarify
# Answer the generated clarification questions in .driftline/.
driftline finalize
driftline check
```

`init` creates `vision.md` and local configuration, scans the repository and proposes capability/guarantee sections. `clarify` collects questions, and `finalize` proposes changes based on the answers. `check` compares the current vision with the project meaning model and prints an alignment/drift summary. Proposed edits are written under `.driftline/tmp/` and opened for review with the editor integration.

For example, a synthetic vision might say “Expose a read-only lookup API.” A drift response can identify a new write capability and propose updated wording. This explains the response format; it is not a measured model result.

**Runtime:** reasoning commands require [Ollama](https://ollama.com/) and a local model. They can launch an installer when Ollama is missing and pull large model files. Install and configure Ollama deliberately before running them; `--help` and the offline tests do neither. VS Code's `code` CLI is used for the diff workflow; inspect `core/vision/diff.py` for platform fallbacks. `install-hook` writes a Git pre-commit hook; the current check is advisory and is not a reliable blocking quality gate.

## How it works

| Layer | Responsibility |
|---|---|
| `core/structure/` | Extract Python classes, sync/async functions, imports and calls; merge per-file graphs |
| `core/pmm/` | Reconcile structural evidence and model interpretations into a project meaning model |
| `core/vision/` | Load intent, clarification state and proposed editor diffs |
| `core/drift/` | Validate the comparison response; malformed fields cannot report alignment |
| `core/ai/` | Load packaged prompt resources and run the model adapter |
| `cli/` | Present the workflow and manage local state |

## Privacy and limits

The scanner always excludes `.git`, `.driftline`, common virtual environments/caches, `node_modules` and `.env*` paths, including nested ones. Add project-specific globs in `.driftline/config.json` under `ignore_paths`. It does **not** automatically honor `.gitignore` and is not a secret detector; review exclusions before using it on confidential repositories. Keep `.driftline/` private.

Python has structural parsing; other languages receive file placeholders. Invalid Python yields an empty graph. Symbols are simplified and not a complete call graph or type analysis. Local model reasoning is nondeterministic, can miss behavior, and must be reviewed. There is no hosted product, production service or demonstrated accuracy benchmark in this release.

## Offline verification

```sh
python -m pip install -r requirements-dev.txt
python -m pytest -q
python -m build --wheel
python -m pip install --no-deps dist/driftline-0.1.1-py3-none-any.whl
python tests/check_installed.py
python -m pip_audit -r requirements.txt
```

[CI](https://github.com/C-X1an/driftline/actions) runs offline behavior tests and installs the wheel outside the checkout on Linux and Windows. Tests cover async extraction, scan exclusions, blank vision, malformed model responses, CLI help and packaged prompts. They mock model calls and do not validate a real model's semantic accuracy.

Licensed under [MIT](LICENSE).
