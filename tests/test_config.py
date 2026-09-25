"""Config loading: the repo's config/ariel.toml is valid, and bad keys fail loudly."""

import pytest

from ariel.config import DEFAULT_CONFIG_PATH, ConfigError, load_config, parse_config

REPO_TOML = DEFAULT_CONFIG_PATH.read_text(encoding="utf-8")


def test_repo_config_loads() -> None:
    config = load_config()
    assert "send" in config.safety.confirm


def test_unknown_key_fails() -> None:
    text = REPO_TOML.replace("[stt]\n", '[stt]\nmodle = "small"\n')
    with pytest.raises(ConfigError, match="stt.modle"):
        parse_config(text)


def test_missing_key_fails() -> None:
    text = REPO_TOML.replace('language = "en"\n', "")
    with pytest.raises(ConfigError, match="stt.language"):
        parse_config(text)
