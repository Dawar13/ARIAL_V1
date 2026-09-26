"""Local model smoke test (task 0.4): structured extraction through Ollama, five runs.

Run with: uv run python scripts/smoke_llm.py
Uses the model in [models] local, and writes latency and tokens per second to docs/hardware.md.
Exits with status 1 unless all five replies match the schema.
"""

import sys
from datetime import date

from hardware_doc import write_section
from pydantic import BaseModel, ValidationError

from ariel.brain.local import extract
from ariel.config import load_config

COMMAND = "send a mail to Rahul saying the demo moved to five"
SYSTEM = (
    "Extract the email the user wants to send. recipient is who it goes to, subject is a short "
    "subject line you write, and body is the message text."
)
RUNS = 5


class MailCommand(BaseModel):
    recipient: str
    subject: str
    body: str


if __name__ == "__main__":
    model = load_config().models.local
    if not model:
        sys.exit("Set [models] local in config/ariel.toml first.")
    rows, valid = [], 0
    for run in range(1, RUNS + 1):
        try:
            mail, stats = extract(model, COMMAND, MailCommand, system=SYSTEM)
        except ValidationError as exc:
            print(f"run {run}: reply did not match the schema: {exc}")
            rows.append(f"| {run} | no match | | | | |")
            continue
        valid += 1
        print(
            f"run {run}: {mail.model_dump()} in {stats.total_s:.1f} s "
            f"(load {stats.load_s:.1f} s), {stats.tokens_per_second:.1f} tokens/s"
        )
        rows.append(
            f"| {run} | {mail.recipient}; {mail.subject}; {mail.body} | {stats.total_s:.1f} "
            f"| {stats.load_s:.1f} | {stats.prompt_tokens} in, {stats.output_tokens} out "
            f"| {stats.tokens_per_second:.1f} |"
        )
    body = "\n".join(
        [
            "## Local model",
            "",
            f"Measured on {date.today().isoformat()} by `scripts/smoke_llm.py` with `{model}` "
            f'on the CPU: extract recipient, subject and body from "{COMMAND}".',
            "Run 1 includes loading the model from disk; later runs reuse it.",
            f"Result: {valid} of {RUNS} replies matched the schema.",
            "",
            "| Run | Extracted (recipient; subject; body) | Total s | Load s | Tokens | Tokens/s |",
            "|---|---|---|---|---|---|",
            *rows,
        ]
    )
    write_section("smoke_llm.py", body)
    print(f"{valid} of {RUNS} replies matched the schema; written to docs/hardware.md")
    sys.exit(0 if valid == RUNS else 1)
