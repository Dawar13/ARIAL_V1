"""Text to speech smoke test (task 0.5): "Ariel is ready." in three Kokoro voices.

Run with: uv run python scripts/smoke_tts.py [voice ...]
Listen, pick one, and put its name in [tts] voice in config/ariel.toml.
Voice names start with a (American) or b (British), then f or m for female or male.
"""

import sys
import time

from ariel.config import load_config
from ariel.voice.tts import engine, render, speak

TEXT = "Ariel is ready."
DEFAULT_VOICES = ["af_heart", "bf_emma", "bm_george"]

if __name__ == "__main__":
    config = load_config()
    voices = sys.argv[1:] or DEFAULT_VOICES
    for voice in voices:
        kokoro = engine(config.tts, voice)
        started = time.perf_counter()
        speech = render(TEXT, kokoro)
        seconds = len(speech.audio) / (speech.sample_rate * speech.sample_width * speech.channels)
        took = time.perf_counter() - started
        print(f"{voice}: synthesised {seconds:.1f} s of audio in {took:.1f} s")
        print(f"  playing {voice}...")
        speak(TEXT, kokoro, config.tts)
        time.sleep(0.5)
    print("\nPick a voice and set it in [tts] voice in config/ariel.toml.")
