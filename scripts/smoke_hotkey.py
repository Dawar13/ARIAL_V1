"""Hotkey smoke test (task 0.5): the trigger hotkey prints "triggered", the kill hotkey "kill".

Run with: uv run python scripts/smoke_hotkey.py
Click into another app (Notepad, Chrome) and press both hotkeys a few times.
Stops after 60 seconds, or press Ctrl+C here.
"""

import time

from ariel.config import load_config
from ariel.voice.trigger import hotkeys

SECONDS = 60

if __name__ == "__main__":
    trigger = load_config().trigger
    listener = hotkeys(
        trigger,
        on_trigger=lambda: print(f"{time.strftime('%H:%M:%S')} triggered", flush=True),
        on_kill=lambda: print(f"{time.strftime('%H:%M:%S')} kill", flush=True),
    )
    print(f"Listening for {trigger.hotkey} and {trigger.kill_hotkey} for {SECONDS} s...")
    try:
        time.sleep(SECONDS)
    except KeyboardInterrupt:
        pass
    finally:
        listener.stop()
    print("Stopped.")
