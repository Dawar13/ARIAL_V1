"""Health checks behind `ariel doctor`. No check ever performs an irreversible action.

Each check runs in its own daemon thread with a timeout, so one hung component cannot hang
the doctor. A check returns a short detail when it passes and raises when it fails.
"""

import os
import shutil
import subprocess
import sys
import threading
import time
from collections.abc import Callable
from dataclasses import dataclass

from pydantic import BaseModel

from ariel.brain.local import installed_models
from ariel.config import REPO_ROOT, Config, ConfigError, load_config
from ariel.hands.gateway import McpServerConfig, list_tools, load_mcp_servers
from ariel.hands.google_auth import GoogleAuthError, client_file, load_credentials


class CheckResult(BaseModel):
    """One row of the doctor's report."""

    name: str
    ok: bool
    detail: str
    hint: str
    seconds: float


class CheckFailed(Exception):
    """A check failed with a known cause; the message replaces the check's default hint."""


@dataclass(frozen=True)
class Check:
    name: str
    run: Callable[[], str]
    hint: str
    loads_model: bool = False


def _python_and_uv() -> str:
    uv = shutil.which("uv")
    if uv is None:
        raise CheckFailed("uv is not on PATH: install it from https://docs.astral.sh/uv/")
    uv_version = subprocess.run([uv, "--version"], capture_output=True, text=True, check=True)
    python = sys.version.split()[0]
    if not python.startswith("3.12."):
        raise CheckFailed(f"Python {python} found; Ariel needs 3.12. Run `uv sync`.")
    return f"Python {python}, uv {uv_version.stdout.split()[1]}"


def _disk(config: Config) -> str:
    free_gb = shutil.disk_usage(REPO_ROOT).free / 1024**3
    if free_gb < config.doctor.min_free_disk_gb:
        raise CheckFailed(
            f"Only {free_gb:.1f} GB free; models need at least {config.doctor.min_free_disk_gb} GB."
        )
    return f"{free_gb:.1f} GB free on {REPO_ROOT.drive}"


def _ollama(config: Config) -> str:
    try:
        models = installed_models()
    except Exception as exc:
        raise CheckFailed(
            "Ollama is not running: start it from the Start menu, or run `ollama serve`."
        ) from exc
    if config.models.local not in models:
        raise CheckFailed(f"Model missing: run `ollama pull {config.models.local}`.")
    return f"running, {config.models.local} present"


def _mcp_server(name: str, server: McpServerConfig, timeout_s: float) -> Callable[[], str]:
    def check() -> str:
        with open(os.devnull, "w") as quiet:
            info = list_tools(server, timeout_s=timeout_s, errlog=quiet)
        return f"started, {len(info.tools)} tools"

    return check


def _google() -> str:
    if not client_file().exists():
        raise CheckFailed(f"OAuth client missing: do the task 0.6 setup and save {client_file()}.")
    try:
        load_credentials()
    except GoogleAuthError as exc:
        raise CheckFailed(str(exc)) from exc
    return "token present and refreshed"


def _gpu(config: Config) -> str:
    if config.stt.device != "cuda":
        return "not needed: [stt] device is cpu"
    if shutil.which("nvidia-smi") is None:
        raise CheckFailed(
            "[stt] device is cuda but nvidia-smi is missing: install the NVIDIA driver."
        )
    subprocess.run(["nvidia-smi"], capture_output=True, check=True, timeout=30)
    return "NVIDIA GPU visible"


def checks(config: Config) -> list[Check]:
    """Every check, in the order the report shows them."""
    timeout = config.doctor.check_timeout_s
    result = [
        Check("Python and uv", _python_and_uv, "Run `uv sync` from the repo folder."),
        Check("Free disk", lambda: _disk(config), "Free some disk space."),
        Check("GPU", lambda: _gpu(config), "Check the NVIDIA driver."),
        Check("Ollama", lambda: _ollama(config), "Start Ollama from the Start menu."),
    ]
    for name, server in load_mcp_servers().items():
        hint = f"Run `uv run python scripts/mcp_probe.py {name}` to see the server's errors."
        result.append(Check(f"MCP: {name}", _mcp_server(name, server, timeout), hint))
    result.append(Check("Google token", _google, "Run `uv run python scripts/smoke_google.py`."))
    return result


def _run(check: Check, timeout_s: float) -> CheckResult:
    outcome: dict[str, object] = {}

    def target() -> None:
        try:
            outcome["detail"] = check.run()
        except BaseException as exc:  # reported in the row, never raised
            outcome["error"] = exc

    start = time.perf_counter()
    thread = threading.Thread(target=target, daemon=True)
    thread.start()
    thread.join(timeout_s)
    seconds = time.perf_counter() - start
    if thread.is_alive():
        return CheckResult(
            name=check.name, ok=False, detail=f"timed out after {timeout_s:.0f} s",
            hint=check.hint, seconds=seconds,
        )  # fmt: skip
    error = outcome.get("error")
    if error is None:
        return CheckResult(
            name=check.name, ok=True, detail=str(outcome["detail"]), hint="", seconds=seconds
        )
    hint = str(error) if isinstance(error, CheckFailed) else check.hint
    detail = "failed" if isinstance(error, CheckFailed) else f"{type(error).__name__}: {error}"
    return CheckResult(name=check.name, ok=False, detail=detail, hint=hint, seconds=seconds)


def run_checks(quick: bool = False) -> list[CheckResult]:
    """Run every check. With quick, skip the ones that load a model."""
    try:
        config = load_config()
    except ConfigError as exc:
        first_line = str(exc).splitlines()[0]
        return [CheckResult(name="Config", ok=False, detail=first_line, hint=str(exc), seconds=0)]
    results = [CheckResult(name="Config", ok=True, detail="loads", hint="", seconds=0)]
    for check in checks(config):
        if quick and check.loads_model:
            continue
        results.append(_run(check, config.doctor.check_timeout_s + 5))
    return results
