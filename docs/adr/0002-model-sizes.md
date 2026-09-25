# 0002: Model sizes

- Status: accepted
- Date: 2026-09-26
- Phase: 0, task 0.2

## Context

From `docs/hardware.md`: an Intel Core i5-1235U (10 cores, 2 performance and 8 efficiency, 12 threads), 12 GB of RAM (11.7 GB usable), Intel Iris Xe integrated graphics and no NVIDIA GPU, so no CUDA. Whisper, Kokoro and the local model all run on the CPU and share system RAM with Windows, Chrome and VS Code. On this laptop, "Whisper and the local model share VRAM" becomes "everything shares 11.7 GB of RAM".

## Options

The phase 0 table's CPU-only row allows Whisper `base` or `small` at int8, and a local model in the 3B to 4B class at 4-bit, which is expected to be slow. For English, the English-only Whisper models (`base.en`, `small.en`) are more accurate than multilingual models of the same size.

## Decision

- Speech to text: faster-whisper `small.en`, device `cpu`, compute type `int8`. This is set in `[stt]`.
- Local model: a 3B to 4B instruct model with tool calling, quantised to 4-bit. Task 0.4 chooses the exact Ollama tag.
- Live partial transcripts (RealtimeSTT's second, "realtime" model) stay off unless task 0.5 shows spare CPU.

Rough memory budget, to be checked in tasks 0.4 and 0.5: Whisper about 0.5 GB, Kokoro about 0.5 GB, and the local model about 3 GB while it is loaded. That is about 4 GB in total, leaving the rest for Windows, Chrome and VS Code.

## Consequences

- `small.en` is chosen over `base.en` for accuracy with names and accented speech. If task 0.5 finds it too slow (the aim is a transcript within about a second of the end of speech), try `distil-small.en`, then `base.en`, and record the change here.
- Tier 1 will be slow on this CPU; task 0.4 measures tokens per second. On this laptop, Tier 0 skills matter even more, and long tasks will go to Tier 2.
- Ollama should unload the local model when it is idle (by default after five minutes), so Chrome and the voice models keep their memory.
- Ollama may be able to use the Iris Xe through its Vulkan backend. Task 0.4 can compare that with the CPU if it needs no extra dependencies.
- On a laptop with an NVIDIA GPU, rerun `scripts/probe_hardware.py` and move up the table.
