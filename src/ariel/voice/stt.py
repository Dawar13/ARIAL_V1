"""Speech to text: the adapter over RealtimeSTT, faster-whisper and PyAudio's device list."""

from typing import Any

import pyaudio
from pydantic import BaseModel
from RealtimeSTT import AudioToTextRecorder

from ariel.config import SttConfig


class AudioDevice(BaseModel):
    index: int
    name: str
    host_api: str
    inputs: int
    outputs: int
    is_default_input: bool
    is_default_output: bool


def audio_devices() -> list[AudioDevice]:
    """Every audio device PyAudio sees, through each Windows host API."""
    audio = pyaudio.PyAudio()
    try:
        default_in = _default_index(audio.get_default_input_device_info)
        default_out = _default_index(audio.get_default_output_device_info)
        devices = []
        for index in range(audio.get_device_count()):
            info = audio.get_device_info_by_index(index)
            devices.append(
                AudioDevice(
                    index=index,
                    name=str(info["name"]),
                    host_api=str(audio.get_host_api_info_by_index(int(info["hostApi"]))["name"]),
                    inputs=int(info["maxInputChannels"]),
                    outputs=int(info["maxOutputChannels"]),
                    is_default_input=index == default_in,
                    is_default_output=index == default_out,
                )
            )
        return devices
    finally:
        audio.terminate()


def _default_index(get_info: Any) -> int | None:
    try:
        return int(get_info()["index"])
    except OSError:
        return None


def device_index(name: str, output: bool = False) -> int | None:
    """PyAudio index of the named device, or None for the Windows default when name is empty."""
    if not name:
        return None
    for device in audio_devices():
        channels = device.outputs if output else device.inputs
        if device.name == name and channels > 0:
            return device.index
    kind = "output" if output else "input"
    raise ValueError(f"No {kind} audio device named {name!r}; run scripts/list_audio.py")


def recorder(stt: SttConfig, **options: Any) -> AudioToTextRecorder:
    """A RealtimeSTT recorder set up from [stt]; extra options go straight to RealtimeSTT."""
    settings: dict[str, Any] = {
        "model": stt.model,
        "device": stt.device,
        "compute_type": stt.compute_type,
        "language": stt.language,
        "spinner": False,
        "no_log_file": True,
    }
    if options.get("use_microphone", True):
        settings["input_device_index"] = device_index(stt.input_device)
    return AudioToTextRecorder(**(settings | options))
