"""MCP adapter: the only module that imports the MCP Python SDK.

Phase 0 uses the client side only: start a server from .mcp.json and list its tools, for
scripts/mcp_probe.py and ariel doctor. The gateway between brain and hands comes in Phase 2.
"""

import json
import sys
from pathlib import Path
from typing import Any, Literal, TextIO

import anyio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import get_default_environment, stdio_client
from mcp.types import PaginatedRequestParams, Tool
from pydantic import BaseModel, ConfigDict

from ariel.config import REPO_ROOT

MCP_CONFIG_PATH = REPO_ROOT / ".mcp.json"


class McpServerConfig(BaseModel):
    """One entry under "mcpServers" in .mcp.json."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    type: Literal["stdio"] = "stdio"
    command: str
    args: tuple[str, ...] = ()
    env: dict[str, str] = {}


class McpTool(BaseModel):
    """One tool a server offers."""

    model_config = ConfigDict(frozen=True)

    name: str
    title: str | None
    description: str
    input_schema: dict[str, Any]
    annotations: dict[str, Any]  # MCP hints such as readOnlyHint, when the server gives them


class McpServerInfo(BaseModel):
    """What a server reported about itself when it started, and its tools."""

    model_config = ConfigDict(frozen=True)

    name: str
    version: str
    tools: tuple[McpTool, ...]


def load_mcp_servers(path: Path = MCP_CONFIG_PATH) -> dict[str, McpServerConfig]:
    """Read the MCP servers configured in .mcp.json."""
    data = json.loads(path.read_text(encoding="utf-8"))
    return {
        name: McpServerConfig.model_validate(entry) for name, entry in data["mcpServers"].items()
    }


def list_tools(
    server: McpServerConfig, timeout_s: float = 120, errlog: TextIO = sys.stderr
) -> McpServerInfo:
    """Start the server, list its tools and stop it. Raises TimeoutError after timeout_s."""
    return anyio.run(_list_tools, server, timeout_s, errlog)


async def _list_tools(server: McpServerConfig, timeout_s: float, errlog: TextIO) -> McpServerInfo:
    params = StdioServerParameters(
        command=server.command,
        args=list(server.args),
        env={**get_default_environment(), **server.env},
    )
    tools: list[Tool] = []
    with anyio.fail_after(timeout_s):
        async with stdio_client(params, errlog=errlog) as (read, write):
            async with ClientSession(read, write) as session:
                init = await session.initialize()
                cursor = None
                while True:
                    page_params = PaginatedRequestParams(cursor=cursor) if cursor else None
                    page = await session.list_tools(params=page_params)
                    tools.extend(page.tools)
                    cursor = page.next_cursor
                    if not cursor:
                        break
    return McpServerInfo(
        name=init.server_info.name,
        version=init.server_info.version,
        tools=tuple(_tool(tool) for tool in tools),
    )


def _tool(tool: Tool) -> McpTool:
    annotations = tool.annotations
    return McpTool(
        name=tool.name,
        title=tool.title,
        description=tool.description or "",
        input_schema=tool.input_schema,
        annotations=annotations.model_dump(by_alias=True, exclude_none=True) if annotations else {},
    )
