# 0006: Wake-word route for "Ariel wake up"

- Status: proposed; the owner decides in Phase 1
- Date: 2026-09-26
- Phase: 0, task 0.5

## Context

Phase 0 proves the wake pipeline with openWakeWord's pre-trained "hey jarvis" model (through RealtimeSTT). Phase 1 needs a custom model for "Ariel wake up". Training is the slowest step of Phase 1, so the route should be chosen early. This laptop has no NVIDIA GPU (`docs/hardware.md`).

## Options

1. **openWakeWord custom model.**
   - Code is Apache 2.0. Training uses openWakeWord's own notebooks: a simple Google Colab notebook that its README says takes under an hour, or a detailed notebook for more control. Both generate synthetic speech with text to speech, and need several thousand negative examples.
   - Training needs a GPU and Linux, which Colab provides, so the missing local NVIDIA GPU does not block it. WSL2 is not needed. Ariel still runs the finished model natively on Windows, through onnxruntime.
   - The model file is ours, runs fully offline and costs nothing.
   - The last openWakeWord release is v0.6.0 (February 2024). The code works, but it is not actively released.
   - openWakeWord's pre-trained models, including "hey jarvis", are licensed CC BY-NC-SA 4.0 (non-commercial). That is acceptable for the Phase 0 placeholder, but not for a product.
2. **Porcupine custom keyword (Picovoice).**
   - You type the phrase and get a model within seconds. Accuracy is strong.
   - It needs a Picovoice AccessKey, and the engine contacts Picovoice's servers to validate the key and check plan limits. That works against "local by default".
   - Current terms: the free plan was only for personal, non-commercial projects, and a Home Assistant community report says Picovoice ended the free tier on 30 June 2026 and disabled existing free keys. The owner should check Picovoice's pricing page before choosing this. It likely means a paid plan.

## Recommendation (for the owner's decision)

Option 1, openWakeWord trained in Colab. It is free, offline and ours, and it fits the architecture. Porcupine remains the fallback if the custom model misses too often or triggers falsely in Phase 1 tests. Training can start now in parallel. It needs only the phrase and roughly an hour of Colab time.

## Consequences

- Phase 1 adds the trained `.onnx` model under `models/` (gitignored, like all model weights) and points `[trigger] wake_model` at it.
- The licence audit (task 0.8) flags the CC BY-NC-SA licence of the pre-trained placeholder models.
