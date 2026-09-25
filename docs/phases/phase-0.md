# Phase 0: Foundations

## Goal

Every borrowed component is installed on the owner's laptop and proven to work, a health-check command shows it, and there is a decision on which open-source agent loop becomes Ariel's brain base. No Ariel logic is written in this phase.

## Rules for this phase

- Follow `CLAUDE.md`, especially the safety rules and dependency rules.
- Check every install command against the project's current README before running it. The commands here were right when written, but projects change.
- Steps marked **HUMAN** need the owner. Stop, say exactly what they must do, and wait.
- Pin versions once something works: `uv.lock` for Python, and exact versions instead of `@latest` in `.mcp.json`.
- All file writes during tests go to `sandbox/`.

## Prerequisites (HUMAN)

The owner installs these. Claude Code checks versions (`git --version`, `uv --version`, `node --version`, `ollama --version`) and reports what is missing. Anything that raises an admin prompt is done by the owner.

- Windows 11
- Git
- uv
- Node.js LTS (for npx-based MCP servers)
- Ollama for Windows
- Google Chrome (the profile the owner uses daily)
- NVIDIA driver, if the laptop has an NVIDIA GPU
- Claude Code running natively on Windows, opened in the repo folder
- Microphone and speakers or headphones; microphone access for desktop apps switched on in Windows Settings > Privacy and security > Microphone

## Tasks

### 0.1 Scaffold the repo

- `git init`. `.gitignore` covers `.env`, `secrets/`, `logs/`, `models/`, `sandbox/`, `.bakeoff/`, `*.wav`, `__pycache__/`, `.venv/`.
- `uv init --package` with src layout, package `ariel`, `requires-python = ">=3.12,<3.13"`.
- Dev dependencies: ruff, pytest, pre-commit.
- In `pyproject.toml`:
  - ruff: line length 100; rules E, F, I, UP, B.
  - pytest: a `desktop` marker, skipped unless run with `-m desktop`.
- `.pre-commit-config.yaml`: ruff check, ruff format, trailing whitespace, end of file, check for large added files, and gitleaks for secrets.
- Create the directory layout from `CLAUDE.md`, with empty modules that each have a one-line docstring.
- `config/ariel.toml` with the skeleton below.
- `src/ariel/config.py` loads the TOML (stdlib `tomllib`) into pydantic models and fails loudly on unknown or missing keys.
- `.env.example` with `ARIEL_CLOUD_PROVIDER=` and `ARIEL_CLOUD_API_KEY=` (used only for the bake-off in this phase).
- `README.md`: five lines pointing to `CLAUDE.md`.
- `sandbox/` folder, gitignored.

```toml
[trigger]
hotkey = "<ctrl>+<alt>+space"
kill_hotkey = "<ctrl>+<alt>+k"
wake_phrase = "ariel wake up"
wake_model = ""            # placeholder in 0.5, custom model in Phase 1
wake_threshold = 0.5

[stt]
model = ""                 # set in 0.2 from docs/hardware.md
device = "cuda"            # or "cpu"
compute_type = "float16"   # "int8" on CPU
language = "en"
input_device = ""          # set in 0.5 if the default is wrong

[tts]
engine = "kokoro"
voice = ""                 # chosen in 0.5
output_device = ""

[models]
local = ""                 # exact Ollama tag, chosen in 0.4
cloud_provider = ""        # Phase 2
cloud_model = ""           # Phase 2
daily_cost_cap_inr = 100

[safety]
sandbox_dir = "sandbox"
confirm = ["send", "reply", "forward", "delete", "trash", "move", "overwrite",
           "pay", "purchase", "post", "submit", "install", "uninstall",
           "system_settings", "close_unsaved"]

[paths]
logs = "logs"
models = "models"
secrets = "secrets"
```

**Acceptance:**
- `uv sync` succeeds.
- `uv run pytest` passes, with at least one test that the config loads and one that a bad key fails.
- `uv run pre-commit run --all-files` passes.
- `git status` shows no ignored paths tracked.

### 0.2 Hardware probe and model sizes

`scripts/probe_hardware.py` writes `docs/hardware.md` with the Windows version and build, CPU, RAM, GPU name, VRAM, and whether CUDA is available (via `nvidia-smi` if present).

Choose sizes from this table. Whisper and the local model share VRAM, so leave 1 to 2 GB of headroom.

| VRAM | Whisper (faster-whisper) | Local model (Ollama, 4-bit) |
|---|---|---|
| None, CPU only | `base` or `small`, int8 | 3B to 4B class; expect it to be slow |
| 6 to 8 GB | `small` or `medium`, float16 | 7B to 8B class |
| 12 GB or more | `large-v3-turbo`, float16 | up to 14B class |

Set `[stt]` in the config. Write `docs/adr/0002-model-sizes.md`.

**Acceptance:** `docs/hardware.md` exists, `[stt]` is set, and ADR 0002 is written.

### 0.3 Hands: Windows-MCP and Playwright MCP

Create `.mcp.json` at the repo root:

```json
{
  "mcpServers": {
    "windows-mcp": {
      "type": "stdio",
      "command": "uvx",
      "args": ["windows-mcp"]
    },
    "playwright": {
      "type": "stdio",
      "command": "cmd",
      "args": ["/c", "npx", "-y", "@playwright/mcp@latest", "--extension"]
    }
  }
}
```

**HUMAN:**
- Install "Playwright Extension" from the Chrome Web Store in the daily Chrome profile.
- Restart Claude Code in the repo and approve both servers when prompted.
- If the extension asks for approval on every connection, put its token in the user environment variable `PLAYWRIGHT_MCP_EXTENSION_TOKEN`, not in `.mcp.json`.

If a server times out on first launch while packages download, raise the `MCP_TIMEOUT` environment variable (milliseconds), for example to 60000.

Smoke tests. Claude Code runs these with the owner watching, and states each action before taking it:
- **a.** Windows-MCP: open Notepad, type "Ariel phase 0 smoke test", save as `sandbox/smoke_notepad.txt`, close Notepad. Then read the file from disk to confirm the contents.
- **b.** Windows-MCP: open File Explorer at `sandbox/`, read its UI tree, and report how many elements it sees and the names of five of them.
- **c.** Playwright MCP: in the owner's Chrome, open YouTube search results for "Ariel The Tempest" and report the first three video titles.

Then:
- Write `scripts/mcp_probe.py` using the MCP Python SDK. It starts each server from `.mcp.json`, lists its tools, and writes `docs/tools/windows-mcp.md` and `docs/tools/playwright.md` (tool names, descriptions, input schemas). This is the reference for Phases 1 and 2, and `ariel doctor` reuses it.
- Replace `@latest` with the version that worked, and record the Windows-MCP version.

**Acceptance:**
- Smoke tests a, b and c pass.
- Both tool lists are written.
- Versions are pinned.

### 0.4 Local model

- Pull the model size chosen in 0.2. Check the Ollama library for the current best small instruct model with tool calling in that size class, for example the Qwen3 family or newer. Record the exact tag in `[models] local`.
- `scripts/smoke_llm.py` uses the `ollama` Python package to:
  - extract a pydantic schema (`recipient`, `subject`, `body`) from "send a mail to Rahul saying the demo moved to five", using Ollama structured outputs;
  - measure latency and tokens per second, and append both to `docs/hardware.md`.

**Acceptance:** valid JSON matching the schema in 5 of 5 runs.

### 0.5 Voice in and out

- Install `realtimestt[faster-whisper,openwakeword]`, RealtimeTTS with its Kokoro engine (check the README for the exact extra), and `pynput`.
- CUDA: faster-whisper needs matching CUDA and cuDNN libraries on Windows. Follow RealtimeSTT's CUDA notes. If it fights, run on CPU with int8 for now, and log that in the phase report.

Scripts:
- `scripts/list_audio.py`: lists input and output devices, appends them to `docs/hardware.md`, and sets the device fields in the config if the defaults are wrong.
- `scripts/smoke_stt.py`: records until silence (voice activity detection) and prints the transcript and latency.
  - **HUMAN:** say five sentences, including "search YouTube for lo-fi music", "open Notepad" and "send a mail to Rahul saying I will be late".
- `scripts/smoke_tts.py`: speaks "Ariel is ready." in three Kokoro voices.
  - **HUMAN:** pick one. Record it in `[tts] voice`.
- `scripts/smoke_hotkey.py`: the configured hotkey prints "triggered" and the kill hotkey prints "kill", even while another app has focus.
- `scripts/smoke_wake.py`: openWakeWord with a pre-trained placeholder model (openWakeWord ships "hey jarvis") proves the wake pipeline end to end. The custom "Ariel wake up" model is Phase 1 work.

Write `docs/adr/0006-wake-word-route.md` listing the two options for the custom phrase. The decision can wait for Phase 1.
- **openWakeWord custom model:** trained with a pinned training setup. It needs an NVIDIA GPU and Linux or WSL2 for training only. Ariel itself still runs natively.
- **Porcupine custom keyword:** needs a Picovoice access key. Check its current terms.

Training is the slowest step of Phase 1, so the owner may choose to start it now in parallel.

**Acceptance:**
- 5 of 5 transcripts are usable.
- A voice is chosen.
- Both hotkeys fire with any app focused.
- The placeholder wake word triggers 5 of 5 times at normal distance.
- No false triggers during 5 minutes of normal talk or music.

### 0.6 Google access (Gmail and Calendar)

Decision: use Google's official Python client, not a third-party MCP server. It has fewer moving parts, allows least-privilege scopes, and it is what the Phase 1 skills will call. Record this in `docs/adr/0005-google-access.md`.

**HUMAN**, in Google Cloud Console:
1. Create a project named "ariel".
2. Enable the Gmail API and the Google Calendar API.
3. Configure the OAuth consent screen: External, Testing mode, with the owner's address as a test user.
4. Create an OAuth client ID of type "Desktop app".
5. Download the JSON to `secrets/google_client.json`.

Build:
- Scopes (least privilege): `gmail.readonly`, `gmail.compose` (drafts and sending, which the gate will control from Phase 1), `calendar.readonly`.
- `src/ariel/hands/google_auth.py`: the desktop OAuth flow. The token is stored with `keyring`, never as a file on disk.
- In Testing mode, Google refresh tokens expire after about seven days. `ariel doctor` must detect an expired token and tell the owner to sign in again.
- `scripts/smoke_google.py`:
  - prints the subjects of the five latest inbox mails and today's calendar events;
  - creates one draft to the owner's own address with the subject "Ariel phase 0 draft" and does not send it.
- **HUMAN:** check the draft in Gmail, then delete it yourself.

**Acceptance:**
- Subjects and events print.
- The draft is visible in Gmail.
- No token file exists on disk.

### 0.7 Bake-off: choose the brain base

Purpose: decide whether Windows-Use or Operator-Use becomes the agent loop Ariel wraps in Phase 2, or whether Operator-Use is close enough to fork.

Setup:
- Install each one in its own throwaway environment under `.bakeoff/`, following its README. Neither is added to Ariel's dependencies.
- **HUMAN:** put one cloud API key in `.env`, from a provider both frameworks support. Set a small spending limit in the provider's dashboard, for example ₹500. Both frameworks use the same model and the same step limit.
- **HUMAN:** before the runs, close anything sensitive (banking, private chats). These agents act on the real desktop. Watch every run and stop it if needed.

Tasks go in `evals/bakeoff/tasks.yaml`. All are read-only or confined to `sandbox/`:
1. Open Notepad, type "bake-off one", save as `sandbox/bakeoff1.txt`.
2. Open Calculator, compute 18% of 84,500, and report the result.
3. In File Explorer, open `sandbox/` and create a folder named "reports".
4. Open Settings and report the Windows version and build.
5. In Chrome, search YouTube for "Andrej Karpathy intro to large language models" and report the first result's title and channel.
6. In Chrome, find today's weather in Mumbai and report the temperature.
7. Open VS Code and open the ariel repo folder. This tests an Electron app.
8. Find the largest file in the Downloads folder and report its name and size.
9. Copy the first paragraph of the Wikipedia article "Ariel (The Tempest)" into a new Notepad file saved as `sandbox/bakeoff9.txt`.
10. In Gmail in Chrome, create a draft to the owner's own address with the subject "bake-off draft". Do not send it.

For every task and framework, record:
- success (the owner judges);
- steps;
- wall time;
- tokens and cost;
- owner interventions;
- crashes.

Then read each codebase and assess:
- licence;
- last release date and commit activity;
- whether it can run as a library inside our process;
- **whether every action can be intercepted before it executes**;
- whether it accepts MCP servers or custom tools;
- whether the model can be swapped per step (needed for tiers);
- code quality.

Write `docs/adr/0004-brain-base.md` with the results table and the decision. Interception is a hard requirement: a framework whose actions cannot be intercepted before they execute is rejected, even if it scores higher, because the safety gate depends on it.

**Acceptance:**
- All 20 runs are logged.
- ADR 0004 is written.
- The owner decides whether the key stays in `.env` until Phase 2.

### 0.8 Licence audit

- Python dependencies: run `uvx pip-licenses` against the project environment.
- Non-Python components (Playwright MCP, Ollama, Kokoro model weights, openWakeWord models): read the licence from each repo.
- Record each component, its licence and any obligations in `docs/adr/0003-licences.md`. Flag anything that is not MIT, Apache 2.0 or BSD for the owner.

**Acceptance:** every component in the "Borrowed components" table of `CLAUDE.md` has a licence line.

### 0.9 `ariel doctor`

`src/ariel/cli.py` uses typer. `ariel doctor` prints a rich table with one row per check: green or red, plus a one-line fix hint. The idea is borrowed from OpenJarvis's `jarvis doctor`.

Checks:
- Python and uv versions.
- Config loads.
- Microphone and speaker found.
- Speech loop without the microphone: TTS speaks "open notepad" into an audio buffer, Whisper transcribes that buffer, and the transcript must match. RealtimeSTT accepts audio fed by the application.
- Wake model loads.
- Hotkey listener starts.
- Ollama is reachable and the configured model is present.
- Each server in `.mcp.json` starts and lists its tools (reuse `scripts/mcp_probe.py`).
- Google token present and refreshable; an expired token gives the re-sign-in hint.
- GPU visible, if `device = "cuda"`.
- Free disk space for models.

Behaviour:
- Every check has a timeout.
- Doctor never performs an irreversible action.
- `--quick` skips model loads.
- `--json` prints machine-readable output.

**Acceptance:**
- All rows are green on the owner's laptop.
- Stopping Ollama turns exactly that row red, with the right hint.

### 0.10 Close the phase

- ADRs present:
  - 0001: native Windows and core stack
  - 0002: model sizes
  - 0003: licences
  - 0004: brain base
  - 0005: Google access
  - 0006: wake-word route
- `docs/phases/phase-0-report.md` covers:
  - what was done;
  - deviations from this document;
  - measurements: STT latency, local model latency and tokens per second, the bake-off table;
  - open issues;
  - recommendations for Phase 1.
- Update "Current phase" in `CLAUDE.md` to "Phase 0 complete, awaiting Phase 1 document". Then stop.

## Exit checklist

- [ ] `uv sync`, `uv run pytest` and pre-commit all pass
- [ ] `docs/hardware.md` written, model sizes chosen
- [ ] Windows-MCP and Playwright MCP smoke tests pass, tool lists written, versions pinned
- [ ] Local model returns valid structured JSON in 5 of 5 runs
- [ ] Speech to text, voice, hotkeys and placeholder wake word work
- [ ] Gmail read, Calendar read and draft creation work; token stored in Credential Manager
- [ ] Bake-off done, ADR 0004 written
- [ ] Licence audit done
- [ ] `ariel doctor` is all green, and turns red correctly when something breaks
- [ ] Phase 0 report written

## Out of scope for Phase 0

Router, skills, agent loop, safety gate, verifier, tray app, and any code path that sends, deletes or submits. Training the custom wake-word model may start in parallel but is not required to finish this phase.
