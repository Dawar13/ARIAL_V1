"""Spoken replies: the adapter over RealtimeTTS with the Kokoro engine."""

from pydantic import BaseModel
from RealtimeTTS import KokoroEngine, TextToAudioStream

from ariel.config import TtsConfig
from ariel.voice.stt import device_index


class Speech(BaseModel):
    """Audio rendered without playing it: raw PCM chunks joined, and their format."""

    audio: bytes
    sample_rate: int
    channels: int
    sample_width: int  # bytes per sample


def engine(tts: TtsConfig, voice: str = "") -> KokoroEngine:
    """A Kokoro engine with the given voice, or the configured one."""
    chosen = voice or tts.voice
    return KokoroEngine(voice=chosen) if chosen else KokoroEngine()


def speak(text: str, kokoro: KokoroEngine, tts: TtsConfig) -> None:
    """Say `text` through the configured output device and wait until it has finished."""
    stream = TextToAudioStream(kokoro, output_device_index=device_index(tts.output_device, True))
    stream.feed(text)
    stream.play()


def render(text: str, kokoro: KokoroEngine) -> Speech:
    """Synthesise `text` into memory without playing it."""
    chunks: list[bytes] = []
    stream = TextToAudioStream(kokoro, muted=True)
    stream.feed(text)
    stream.play(muted=True, on_audio_chunk=chunks.append)
    _format, channels, sample_rate = kokoro.get_stream_info()
    sample_width = 4 if _format == 1 else 2  # pyaudio.paFloat32 is 1, paInt16 is 8
    return Speech(
        audio=b"".join(chunks),
        sample_rate=sample_rate,
        channels=channels,
        sample_width=sample_width,
    )
