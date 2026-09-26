"""Shared by the probe and smoke scripts: write one script's section of docs/hardware.md."""

from ariel.config import REPO_ROOT

HARDWARE_DOC = REPO_ROOT / "docs" / "hardware.md"


def write_section(script: str, body: str) -> None:
    """Replace the section `script` wrote last time, or append it. Other sections stay as is."""
    begin = f"<!-- BEGIN {script}: generated, rerun the script instead of editing -->"
    end = f"<!-- END {script} -->"
    block = f"{begin}\n{body.rstrip()}\n{end}\n"
    text = HARDWARE_DOC.read_text(encoding="utf-8") if HARDWARE_DOC.exists() else "# Hardware\n"
    if begin in text and end in text:
        before, rest = text.split(begin, 1)
        after = rest.split(end, 1)[1].lstrip("\n")
        text = before + block + (f"\n{after}" if after else "")
    else:
        text = text.rstrip("\n") + "\n\n" + block
    HARDWARE_DOC.write_text(text, encoding="utf-8", newline="\n")
