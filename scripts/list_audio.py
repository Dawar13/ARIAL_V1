"""List audio devices and record them in docs/hardware.md (task 0.5).

Run with: uv run python scripts/list_audio.py [--input NAME] [--output NAME]
With --input or --output, the device name is also written to [stt] input_device or
[tts] output_device in config/ariel.toml. Leave both out to keep the Windows defaults.
"""

import argparse
import re

from hardware_doc import write_section

from ariel.config import DEFAULT_CONFIG_PATH
from ariel.voice.stt import AudioDevice, audio_devices


def set_config_value(key: str, value: str) -> None:
    """Replace `key = "..."` in config/ariel.toml, keeping comments and layout."""
    text = DEFAULT_CONFIG_PATH.read_text(encoding="utf-8")
    pattern = rf'^({key}\s*=\s*)"[^"]*"'
    new_text, count = re.subn(pattern, rf'\g<1>"{value}"', text, count=1, flags=re.MULTILINE)
    if count != 1:
        raise SystemExit(f"{key} not found in {DEFAULT_CONFIG_PATH}")
    DEFAULT_CONFIG_PATH.write_text(new_text, encoding="utf-8", newline="\n")


def row(device: AudioDevice) -> str:
    kind = "input" if device.inputs else "output"
    default = "yes" if device.is_default_input or device.is_default_output else ""
    return f"| {device.index} | {device.name} | {kind} | {device.host_api} | {default} |"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", help="microphone name to store in [stt] input_device")
    parser.add_argument("--output", help="speaker name to store in [tts] output_device")
    args = parser.parse_args()

    # MME is PyAudio's default host API on Windows and lists every device once.
    devices = [d for d in audio_devices() if d.host_api == "MME"]
    body = "\n".join(
        [
            "## Audio devices",
            "",
            "Listed by `scripts/list_audio.py` (MME host API, which PyAudio uses by default).",
            "",
            "| Index | Name | Kind | Host API | Windows default |",
            "|---|---|---|---|---|",
            *(row(device) for device in devices),
        ]
    )
    write_section("list_audio.py", body)
    print(body)
    if args.input:
        set_config_value("input_device", args.input)
        print(f"[stt] input_device set to {args.input!r}")
    if args.output:
        set_config_value("output_device", args.output)
        print(f"[tts] output_device set to {args.output!r}")
