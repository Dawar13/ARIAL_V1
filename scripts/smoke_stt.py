"""Speech to text smoke test (task 0.5): five spoken sentences, transcript and latency each.

Run with: uv run python scripts/smoke_stt.py
Say one sentence each time you see "Speak now". Recording stops by itself when you pause.
Suggested sentences: "search YouTube for lo-fi music", "open Notepad",
"send a mail to Rahul saying I will be late", and two of your own.
Latency is from the end of your speech to the transcript. Results go to docs/hardware.md.
"""

import time
from datetime import date

from hardware_doc import write_section

from ariel.config import load_config
from ariel.voice.stt import recorder

SENTENCES = 5

if __name__ == "__main__":
    config = load_config()
    stopped_at: list[float] = []
    print(f"Loading {config.stt.model} on {config.stt.device} ({config.stt.compute_type})...")
    started = time.perf_counter()
    with recorder(
        config.stt, on_recording_stop=lambda: stopped_at.append(time.perf_counter())
    ) as rec:
        print(f"Model ready in {time.perf_counter() - started:.1f} s")
        rows = []
        for number in range(1, SENTENCES + 1):
            print(f"\n[{number}/{SENTENCES}] Speak now...")
            text = rec.text()
            latency = time.perf_counter() - stopped_at[-1] if stopped_at else float("nan")
            print(f"  heard: {text!r}  (latency {latency:.2f} s)")
            rows.append(f"| {number} | {text} | {latency:.2f} |")

    body = "\n".join(
        [
            "## Speech to text",
            "",
            f"Measured on {date.today().isoformat()} by `scripts/smoke_stt.py` with "
            f"`{config.stt.model}` on {config.stt.device} ({config.stt.compute_type}). "
            "Latency runs from the end of speech to the transcript.",
            "",
            "| # | Transcript | Latency s |",
            "|---|---|---|",
            *rows,
        ]
    )
    write_section("smoke_stt.py", body)
    print("\nWritten to docs/hardware.md. Check each transcript is usable.")
