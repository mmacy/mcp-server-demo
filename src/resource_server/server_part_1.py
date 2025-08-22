"""
Part 1 (Resource Server): Basic FastMCP server

This module implements the minimal, single-file Resource Server (which is also the MCP server).
It exposes one public tool and runs over the default stdio transport so you can connect
with the MCP Inspector via: `uv run mcp dev resource_server/server.py`.

Tutorial context:

- Added in Part 1
- Service: RS (Resource Server)
- Layer: App (single file for the initial baseline)
- Teaches: FastMCP basics, single-tool server, stdio transport
- Prerequisites: Python basics and ability to run commands with `uv`

Key learning points:

- How to create a FastMCP server with a friendly name and instructions
- How to define a simple tool with type hints and a clear docstring
- How to run the server locally and connect with the MCP Inspector
"""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

# TUTORIAL: Create a single FastMCP instance. In Part 1 we keep the server minimal and
# self-contained. Later parts will refactor structure and add authentication.
mcp = FastMCP(
    name="mcp-demo-resource-server",
    instructions=(
        "Welcome to the Part 1 demo Resource Server. "
        "This server exposes a single public tool you can try from the MCP Inspector."
    ),
)


@mcp.tool(name="greet", title="Greet a user", description="Return a friendly greeting for the provided name.")
def greet(name: str, punctuation: str = "!") -> str:
    """
    Generate a greeting.

    Args:
        name: The name to greet.
        punctuation: Optional punctuation to use at the end of the greeting.

    Returns:
        A friendly greeting that includes the provided name.

    Tutorial note:
        - This is a minimal example of a public tool. Tools must include type hints
          to generate a correct JSON Schema for parameters.
        - In the MCP Inspector, connect to this server and call the 'greet' tool
          with any name to see the response.
    """
    safe_name = name.strip() or "there"
    end = punctuation if punctuation else "!"
    return f"Hello, {safe_name}{end}"


if __name__ == "__main__":
    # TUTORIAL: Run the server using the default stdio transport.
    # Try it:
    #   uv run mcp dev resource_server/server.py
    # In the MCP Inspector, you should see a single tool named "greet".
    mcp.run()
