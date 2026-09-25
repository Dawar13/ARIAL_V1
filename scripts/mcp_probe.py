"""Write each MCP server's tool list from .mcp.json to docs/tools/<server>.md (task 0.3).

Run with: uv run python scripts/mcp_probe.py [server ...]
It only starts each server and lists its tools; it never calls a tool.
The first run can take a minute while uvx and npx download the servers.
"""

import json
import sys
from datetime import date

from ariel.config import REPO_ROOT
from ariel.hands.gateway import McpServerConfig, McpServerInfo, list_tools, load_mcp_servers

TOOLS_DIR = REPO_ROOT / "docs" / "tools"


def render(name: str, server: McpServerConfig, info: McpServerInfo) -> str:
    """Markdown reference for one server's tools."""
    command = " ".join([server.command, *server.args])
    lines = [
        f"# {name} tools",
        "",
        f"Listed on {date.today().isoformat()} by `scripts/mcp_probe.py`, which started the "
        f"server with `{command}` from `.mcp.json`.",
        f"The server reported itself as `{info.name}` version `{info.version}` "
        f"and offered {len(info.tools)} tools.",
        "",
    ]
    for tool in info.tools:
        lines += [f"## {tool.name}", ""]
        if tool.title and tool.title != tool.name:
            lines += [f"Title: {tool.title}", ""]
        description = tool.description.strip() or "(no description)"
        lines += [f"> {line}" if line.strip() else ">" for line in description.splitlines()]
        lines.append("")
        hints = {key: value for key, value in tool.annotations.items() if key != "title"}
        if hints:
            text = ", ".join(f"{key}: {json.dumps(value)}" for key, value in hints.items())
            lines += [f"Hints: {text}", ""]
        schema = json.dumps(tool.input_schema, indent=2, ensure_ascii=False)
        lines += ["Input schema:", "", "```json", schema, "```", ""]
    text = "\n".join(lines)
    return "\n".join(line.rstrip() for line in text.splitlines()).rstrip("\n") + "\n"


if __name__ == "__main__":
    servers = load_mcp_servers()
    TOOLS_DIR.mkdir(parents=True, exist_ok=True)
    for name in sys.argv[1:] or servers:
        print(f"{name}: starting the server and listing its tools...", flush=True)
        info = list_tools(servers[name])
        path = TOOLS_DIR / f"{name}.md"
        path.write_text(render(name, servers[name], info), encoding="utf-8", newline="\n")
        print(f"{name}: {info.name} {info.version}, {len(info.tools)} tools, written to {path}")
