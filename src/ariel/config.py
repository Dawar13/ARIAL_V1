"""Load config/ariel.toml into typed, read-only settings."""

import tomllib
from pathlib import Path
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationError

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG_PATH = REPO_ROOT / "config" / "ariel.toml"


class ConfigError(Exception):
    """The config file is unreadable, is not valid TOML, or has unknown, missing or bad keys."""


class _Table(BaseModel):
    """One TOML table: unknown keys are an error, and values cannot change after loading."""

    model_config = ConfigDict(extra="forbid", frozen=True)


class TriggerConfig(_Table):
    """[trigger]: hotkeys and the wake word."""

    hotkey: str
    kill_hotkey: str
    wake_phrase: str
    wake_model: str
    wake_threshold: Annotated[float, Field(ge=0, le=1)]


class SttConfig(_Table):
    """[stt]: speech to text."""

    model: str
    device: Literal["cuda", "cpu"]
    compute_type: str
    language: str
    input_device: str


class TtsConfig(_Table):
    """[tts]: spoken replies."""

    engine: str
    voice: str
    output_device: str


class ModelsConfig(_Table):
    """[models]: the local and cloud models, and the daily cost cap."""

    local: str
    cloud_provider: str
    cloud_model: str
    daily_cost_cap_inr: Annotated[float, Field(ge=0)]


class SafetyConfig(_Table):
    """[safety]: where test actions may write, and which actions need confirmation."""

    sandbox_dir: Path
    confirm: tuple[str, ...]


class PathsConfig(_Table):
    """[paths]: folders for logs, model files and secrets, relative to the repo root."""

    logs: Path
    models: Path
    secrets: Path


class Config(_Table):
    """The whole of config/ariel.toml."""

    trigger: TriggerConfig
    stt: SttConfig
    tts: TtsConfig
    models: ModelsConfig
    safety: SafetyConfig
    paths: PathsConfig


def load_config(path: Path = DEFAULT_CONFIG_PATH) -> Config:
    """Read and validate the config file. Raises ConfigError naming the file and each bad key."""
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise ConfigError(f"Cannot read config file {path}: {exc}") from exc
    return parse_config(text, source=str(path))


def parse_config(text: str, source: str = "config") -> Config:
    """Validate TOML text against the models above. Raises ConfigError on any problem."""
    try:
        return Config.model_validate(tomllib.loads(text))
    except (tomllib.TOMLDecodeError, ValidationError) as exc:
        raise ConfigError(f"{source} is invalid:\n{exc}") from exc
