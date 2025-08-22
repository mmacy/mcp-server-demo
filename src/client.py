"""
Part 5: Client example for full three-party OAuth flow

This script demonstrates a complete OAuth 2.1 flow between:

- Client (this script)
- Resource Server (RS) providing MCP over Streamable HTTP
- Authorization Server (AS) issuing access tokens

It uses the MCP Python SDK's Streamable HTTP transport and the built-in
OAuth client provider to automatically:
- Discover RS protected resource metadata (RFC 9728)
- Discover AS metadata (RFC 8414)
- Dynamically register the client (RFC 7591)
- Perform Authorization Code + PKCE flow (OAuth 2.1)
- Exchange codes for tokens and authenticate to the RS

Tutorial context:

- Added in Part 5
- Service: Client
- Teaches: Three-party OAuth flow, MCP client patterns, Streamable HTTP transport
- Prerequisites: Running RS (Streamable HTTP) and AS from Parts 3-4

Key learning points:

- Using OAuthClientProvider as httpx.Auth with MCP transports
- Implementing a simple local redirect URI receiver
- Calling public and protected tools via MCP once authenticated

How to run:

1) Terminal 1 - run Authorization Server:
   uv run authorization_server/server.py

2) Terminal 2 - run Resource Server (Streamable HTTP with auth):
   uv run resource_server/server.py
   (Defaults: http://127.0.0.1:8000, MCP path /mcp)

3) Terminal 3 - run client:
   uv run client.py
"""

import logging
import os
import sys
import webbrowser
from typing import Any, Optional, Tuple

import anyio
import httpx
import mcp.types as types
from mcp.client.auth import OAuthClientProvider, OAuthRegistrationError, OAuthTokenError
from mcp.client.session import ClientSession
from mcp.client.streamable_http import MCP_PROTOCOL_VERSION, streamablehttp_client
from mcp.shared._httpx_utils import create_mcp_http_client
from mcp.shared.auth import OAuthClientInformationFull, OAuthClientMetadata, OAuthToken
from pydantic import AnyHttpUrl

# -----------------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------------

# Resource Server base URL and MCP endpoint path
RS_HOST = os.environ.get("RS_HOST", "127.0.0.1")
RS_PORT = int(os.environ.get("RS_PORT", "8000"))
RS_BASE_URL = f"http://{RS_HOST}:{RS_PORT}"
RS_MCP_PATH = os.environ.get("RS_MCP_PATH", "/mcp")
RS_MCP_URL = f"{RS_BASE_URL}{RS_MCP_PATH}"

# Local redirect URI for OAuth flow
OAUTH_REDIRECT_HOST = os.environ.get("OAUTH_REDIRECT_HOST", "127.0.0.1")
OAUTH_REDIRECT_PORT = int(os.environ.get("OAUTH_REDIRECT_PORT", "8765"))
OAUTH_REDIRECT_PATH = os.environ.get("OAUTH_REDIRECT_PATH", "/callback")
OAUTH_REDIRECT_URI = f"http://{OAUTH_REDIRECT_HOST}:{OAUTH_REDIRECT_PORT}{OAUTH_REDIRECT_PATH}"

# -----------------------------------------------------------------------------
# Minimal token storage (in-memory for demo)
# -----------------------------------------------------------------------------


class InMemoryTokenStorage:
    """Simple in-memory storage for tokens and client info."""

    def __init__(self) -> None:
        self._tokens: Optional[OAuthToken] = None
        self._client_info: Optional[OAuthClientInformationFull] = None

    async def get_tokens(self) -> Optional[OAuthToken]:
        return self._tokens

    async def set_tokens(self, tokens: OAuthToken) -> None:
        self._tokens = tokens

    async def get_client_info(self) -> Optional[OAuthClientInformationFull]:
        return self._client_info

    async def set_client_info(self, client_info: OAuthClientInformationFull) -> None:
        self._client_info = client_info


# -----------------------------------------------------------------------------
# Redirect and callback handlers
# -----------------------------------------------------------------------------


async def open_browser_redirect_handler(url: str) -> None:
    """
    Redirect handler that opens the user's default browser.

    Args:
        url: The authorization URL to display to the user.
    """
    print("\nOpening browser for authorization...")
    print(f"If the browser does not open, copy-paste this URL:\n{url}\n")
    try:
        webbrowser.open(url, new=2, autoraise=True)
    except Exception:
        # Fall back to printing only
        pass


async def receive_auth_callback_once() -> Tuple[str, Optional[str]]:
    """
    Start a temporary HTTP server to receive the OAuth authorization code.

    Returns:
        Tuple of (code, state)
    """
    from starlette.applications import Starlette
    from starlette.requests import Request
    from starlette.responses import HTMLResponse
    from starlette.routing import Route
    from uvicorn import Config, Server

    code_state: dict[str, Optional[str]] = {"code": None, "state": None}
    server_ref: dict[str, Any] = {"server": None}

    async def callback_endpoint(request: Request) -> HTMLResponse:
        code = request.query_params.get("code")
        state = request.query_params.get("state")
        code_state["code"] = code if isinstance(code, str) else None
        code_state["state"] = state if isinstance(state, str) else None

        # Signal the server to stop
        server = server_ref.get("server")
        if server is not None:
            server.should_exit = True

        return HTMLResponse(
            "<html><body><h3>Authentication complete.</h3>"
            "<p>You can close this tab and return to the application.</p></body></html>"
        )

    app = Starlette(routes=[Route(OAUTH_REDIRECT_PATH, endpoint=callback_endpoint, methods=["GET"])])

    config = Config(
        app,
        host=OAUTH_REDIRECT_HOST,
        port=OAUTH_REDIRECT_PORT,
        log_level="error",
    )
    server = Server(config)
    server_ref["server"] = server

    async with anyio.create_task_group() as tg:
        tg.start_soon(server.serve)

        # Wait for server to exit after receiving one request
        while not server.should_exit:
            await anyio.sleep(0.05)

        # Server exit requested; cancel task group to clean up
        tg.cancel_scope.cancel()

    if not code_state["code"]:
        raise RuntimeError("Did not receive authorization code")

    return code_state["code"], code_state["state"]


# -----------------------------------------------------------------------------
# Main client logic
# -----------------------------------------------------------------------------


async def run_client() -> int:
    logging.basicConfig(level=logging.INFO)

    # Prepare OAuth client metadata
    client_metadata = OAuthClientMetadata(
        # Starlette will validate this value; we pass a string and pydantic will parse it
        redirect_uris=[AnyHttpUrl(OAUTH_REDIRECT_URI)],
        token_endpoint_auth_method="none",  # Public client (no client secret)
        # grant_types default includes authorization_code and refresh_token
        # response_types default includes "code"
        scope=None,  # Not using scopes in this demo
    )

    storage = InMemoryTokenStorage()

    # Create OAuth provider for httpx
    oauth_auth: httpx.Auth = OAuthClientProvider(
        server_url=RS_MCP_URL,
        client_metadata=client_metadata,
        storage=storage,
        redirect_handler=open_browser_redirect_handler,
        callback_handler=receive_auth_callback_once,
        timeout=300.0,
    )

    # Connect to the Resource Server using Streamable HTTP transport
    # with OAuth2 authentication.
    async with streamablehttp_client(
        url=RS_MCP_URL,
        headers={MCP_PROTOCOL_VERSION: types.LATEST_PROTOCOL_VERSION},
        timeout=30,
        sse_read_timeout=60 * 5,
        terminate_on_close=True,
        httpx_client_factory=create_mcp_http_client,
        auth=oauth_auth,
    ) as (read, write, _get_session_id):
        # Create a MCP client session
        async with ClientSession(read, write) as session:
            print(f"Connecting to MCP server at {RS_MCP_URL}")
            init = await session.initialize()
            print(f"Connected: {init.serverInfo.name} (protocol {init.protocolVersion})")

            # List available tools
            tools = await session.list_tools()
            tool_names = [t.name for t in tools.tools]
            print(f"Available tools: {', '.join(tool_names)}")

            # 1) Call a public tool (if present)
            if "greet" in tool_names:
                print("Calling public tool: greet(name='MCP Learner')")
                result = await session.call_tool("greet", {"name": "MCP Learner"})
                for block in result.content:
                    if isinstance(block, types.TextContent):
                        print(f"greet -> {block.text}")

            # 2) Call a protected tool (requires token)
            if "server_time" in tool_names:
                print("Calling protected tool: server_time()")
                result = await session.call_tool("server_time", {})
                if result.isError:
                    # The server will return error content if tool failed auth
                    print("server_time -> Error:")
                    for block in result.content:
                        if isinstance(block, types.TextContent):
                            print(block.text)
                else:
                    # Expect structured content dict if tool returns structured output
                    if result.structuredContent:
                        print("server_time ->", result.structuredContent)
                    else:
                        for block in result.content:
                            if isinstance(block, types.TextContent):
                                print("server_time ->", block.text)

    return 0


def main() -> int:
    try:
        return anyio.run(run_client)
    except (OAuthRegistrationError, OAuthTokenError) as e:
        print(f"OAuth error: {e}", file=sys.stderr)
        return 2
    except KeyboardInterrupt:
        return 130
    except Exception as e:
        import traceback
        print(f"Unexpected error: {e}", file=sys.stderr)
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
