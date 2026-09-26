"""Wake word smoke test (task 0.5) with openWakeWord's placeholder model "hey jarvis".

Run with: uv run python scripts/smoke_wake.py [minutes]
Two checks, as in the phase document:
  1. Say "hey jarvis" at normal distance five times; each should print a detection.
  2. Run it for five minutes of normal talk or music (`smoke_wake.py 5`); nothing should fire.
After a detection, the recorder transcribes whatever you say next, which also proves the
wake-then-listen pipeline end to end.
"""

import sys
import time

from ariel.config import load_config
from ariel.voice.trigger import wake_recorder

if __name__ == "__main__":
    minutes = float(sys.argv[1]) if len(sys.argv) > 1 else 3
    config = load_config()
    detections: list[str] = []

    def on_wake() -> None:
        detections.append(time.strftime("%H:%M:%S"))
        print(f"{detections[-1]} wake word detected (#{len(detections)})", flush=True)

    print(f"Loading the wake model {config.trigger.wake_model!r} and {config.stt.model}...")
    with wake_recorder(config.stt, config.trigger, on_wake) as rec:
        print(f'Listening for "hey jarvis" for {minutes:g} minutes. Ctrl+C stops early.')
        deadline = time.monotonic() + minutes * 60
        try:
            while time.monotonic() < deadline:
                text = rec.text()
                if text:
                    print(f"  then heard: {text!r}", flush=True)
        except KeyboardInterrupt:
            pass
    print(f"\n{len(detections)} detections: {', '.join(detections) or 'none'}")
