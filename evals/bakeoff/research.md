# Bake-off candidates: desk research (input to ADR 0004)

Collected 2026-09-26 from each project's GitHub repository and PyPI page. Nothing was installed or run. This covers the codebase questions in task 0.7; the 20 bake-off runs are still to come.

Both repositories have moved from CursorTouch to their author's personal account (github.com/Jeomon). Windows-MCP, by the same author, is still at CursorTouch/Windows-MCP. Both frameworks carry their own copy of the Windows UI Automation code rather than using Windows-MCP.

| | Windows-Use | Operator-Use |
|---|---|---|
| Source | github.com/Jeomon/Windows-Use, PyPI `windows-use` | github.com/Jeomon/Operator-Use (branch `operator`), PyPI `operator-use` |
| Licence | MIT | MIT |
| Last release | 0.8.1, 30 Apr 2026; last commit 23 Sep 2026 | PyPI 0.2.9, 23 Mar 2026, an older architecture; git main last committed 9 Jun 2026 |
| Python | 3.10 or newer | git main needs 3.14 or newer, which clashes with Ariel's 3.12 |
| Runs as a library | Yes: `Agent(llm=...).invoke(task)`, synchronous and asynchronous | Yes: `await Runtime.create(RuntimeConfig(...))`, asynchronous only |
| **Intercept every action before it runs** | **Not officially.** Event subscribers see a copy of each tool call but cannot veto it, and their errors are swallowed. Possible only by replacing `agent.registry` with a subclass whose `execute` refuses, which relies on undocumented internals. | **Yes, built in.** `Engine._execute` calls `before_tool_call` before every tool, and it can cancel or rewrite the call. The `tool_call` hooks and guardrails can block. Caveat: a hook that raises is logged and ignored, so the gate must catch its own errors and block. |
| MCP servers and custom tools | No MCP. Tools come from a fixed built-in list. | Yes: `mcp_servers` in settings, tool files, `register_tool` |
| Swap the model per step | Only by reassigning `agent.llm` between steps (unsupported) | Feasible: `engine.llm` is read every turn, and there is a `model_select` event |
| Step limit | `max_steps` (default 25), plus a failure limit and loop guard | None built in; add one through `should_stop_after_turn` or a guardrail |
| Default tools | click, type, app, **shell (arbitrary PowerShell, always on)**, shortcut, scroll, move, wait, scrape, desktop | read, write, edit, **terminal**, process, browser, web, memory, cron, mcp, subagents, messaging channels, and a control centre that can change its own settings |
| Telemetry | **On by default** (PostHog): sends the task text and final answer. Disable with `ANONYMIZED_TELEMETRY=false`. | None found |
| Providers | Anthropic, OpenAI, Google, Ollama and about 10 more | Anthropic, OpenAI, Google, Mistral, Ollama, GitHub Copilot |

## Implications for the bake-off

- Interception is a hard requirement (task 0.7). Operator-Use meets it natively. Windows-Use meets it only through a registry subclass, which should count as "intercept by forking a small part", not as a supported hook.
- Both run a shell tool by default. For the bake-off runs, disable or refuse it where the framework allows, and watch closely.
- Run Windows-Use with `ANONYMIZED_TELEMETRY=false`, otherwise the task text goes to PostHog.
- Operator-Use from git needs Python 3.14 in its own `.bakeoff/` environment. uv can provide that without touching Ariel's 3.12.
- Operator-Use is a large framework (channels, cron, teams, self-reconfiguration). Wrapping it goes against "thin layer" unless most of it is switched off.
