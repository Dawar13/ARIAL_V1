"""Triggers: global hotkeys (pynput) and the wake word (openWakeWord through RealtimeSTT)."""

from collections.abc import Callable
from typing import Any

from pynput import keyboard
from RealtimeSTT import AudioToTextRecorder

from ariel.config import SttConfig, TriggerConfig
from ariel.voice.stt import recorder


def hotkeys(
    trigger: TriggerConfig, on_trigger: Callable[[], None], on_kill: Callable[[], None]
) -> keyboard.GlobalHotKeys:
    """A started listener for the trigger and kill hotkeys; they fire whichever app has focus."""
    listener = keyboard.GlobalHotKeys({trigger.hotkey: on_trigger, trigger.kill_hotkey: on_kill})
    listener.start()
    return listener


def wake_recorder(
    stt: SttConfig, trigger: TriggerConfig, on_wake: Callable[[], None], **options: Any
) -> AudioToTextRecorder:
    """A recorder that waits for the wake word, then records and transcribes one command."""
    return recorder(
        stt,
        wakeword_backend="openwakeword",
        openwakeword_model_paths=trigger.wake_model,
        wake_words=trigger.wake_phrase,
        wake_words_sensitivity=trigger.wake_threshold,
        on_wakeword_detected=on_wake,
        **options,
    )
