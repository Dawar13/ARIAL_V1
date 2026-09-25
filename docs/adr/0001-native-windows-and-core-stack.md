# 0001: Native Windows and core stack

- Status: accepted
- Date: 2026-09-26
- Phase: 0, task 0.1

## Context

Ariel drives native Windows apps through UI Automation, listens on the laptop's microphone, speaks through its speakers and acts inside the owner's logged-in Chrome. UI Automation, the audio devices and that Chrome profile are only fully reachable from native Windows processes. The owner's laptop runs Windows 11 Home; hardware details are in `docs/hardware.md` (task 0.2).

## Options

1. **Native Windows**, with Python managed by uv.
2. **WSL2**, with a bridge back to Windows for UI Automation, audio and Chrome.
3. **A container or virtual machine.**

## Decision

Option 1. The core stack is:

- Python 3.12 (`>=3.12,<3.13`), managed by uv. `uv.lock` pins every Python dependency.
- One package, `ariel`, in a src layout, built with uv's default build backend (`uv_build`).
- Node.js LTS only for npx-based MCP servers (Playwright MCP). Python-based MCP servers (Windows-MCP) run with `uvx`.
- Settings in `config/ariel.toml`, read with the standard library's `tomllib` into frozen pydantic models that reject unknown and missing keys (`ariel.config`).
- Tooling: ruff for linting and formatting (line length 100, rules E, F, I, UP, B); pytest, with tests that touch the real desktop marked `desktop` and skipped by default; pre-commit running ruff, whitespace and end-of-file fixes, a large-file check and gitleaks.
- Secrets only in `.env` or Windows Credential Manager (through keyring), never in the repo.

## Consequences

- Every part of Ariel runs in one operating system with direct access to UI Automation, audio and Chrome. There is no bridge to build or debug.
- Tools that only run on Linux, such as openWakeWord model training, have to run somewhere else. Ariel itself stays native.
- The upper bound on Python means uv resolves for 3.12 only, so a package without wheels for newer Pythons cannot block the lock file. Moving to a newer Python is a separate decision.
- Running Ariel needs Windows 11. Pure logic such as the config loader can still be unit tested anywhere.
