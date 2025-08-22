"""
Part 4 (Resource Server): Tool definitions (content layer)

This module defines the MCP tools exposed by the Resource Server. We moved the tools
out of server.py to keep a clean separation of concerns:

- server.py (app layer): configuration, TokenVerifier wiring, and server setup
- tools.py (content layer): actual tool definitions (public and protected)

Tutorial context:

- Added/refactored in Part 4
- Service: RS (Resource Server)
- Layer: Content (MCP tool definitions)
- Teaches: Public vs. protected tools, per-tool auth checks, context usage
- Prerequisites: Part 1 (single tool), basic understanding of FastMCP

Key learning points:

- Tools can remain simple and focused on business logic
- Protected tools use a TokenVerifier (via the app layer) to validate tokens
- Context gives access to request metadata when using HTTP transports
"""

import datetime
from typing import Any

from mcp.server.auth.provider import TokenVerifier
from mcp.server.fastmcp import Context, FastMCP
from mcp.server.fastmcp.utilities.logging import get_logger

from settings import ResourceServerSettings

logger = get_logger(__name__)


def _extract_bearer_token_from_context(ctx: Context) -> str | None:
    """
    Best-effort extraction of a Bearer token from the HTTP Authorization header.

    TUTORIAL: When running over HTTP transports, the Starlette Request object is
    forwarded in the request context. We read headers directly to support per-tool
    auth checks without globally enforcing auth middleware.

    Returns:
        The raw bearer token string, or None if not present.
    """
    try:
        # The underlying Request (for HTTP transports) is available at:
        # ctx.request_context.request
        req = getattr(ctx.request_context, "request", None)
        # Depending on the transport and SDK version, the attribute may be named `request` or the
        # request object may be stored directly. Handle both.
        request_obj = req if req is not None else ctx.request_context.request
        if request_obj is None or not hasattr(request_obj, "headers"):
            return None

        auth_header = None
        for k, v in request_obj.headers.items():
            if k.lower() == "authorization":
                auth_header = v
                break

        if not auth_header or not auth_header.lower().startswith("bearer "):
            return None
        return auth_header[7:].strip()
    except Exception:
        # If not running over HTTP or no request context exists, just ignore
        return None


async def _require_authenticated(
    ctx: Context,
    verifier: TokenVerifier | None,
    required_scopes: list[str] | None = None,
) -> None:
    """
    Validate that a request is authenticated and optionally enforce scopes.

    Args:
        ctx: FastMCP Context providing access to request metadata.
        verifier: TokenVerifier to validate access tokens with the Authorization Server.
        required_scopes: Optional list of scopes that must be present in the token.

    Raises:
        PermissionError: If token is missing, invalid, or lacks required scopes.

    Tutorial note:
        This demonstrates per-tool protection without globally requiring auth for all
        endpoints. The RS calls the AS only when a protected tool is invoked.
    """
    token = _extract_bearer_token_from_context(ctx)
    if not token:
        raise PermissionError("401 Unauthorized: missing Bearer token")

    if verifier is None:
        # If auth is configured off in settings but a tool still requires it,
        # we fail fast to avoid a false sense of protection.
        raise PermissionError("401 Unauthorized: no verifier configured")

    # SERVICE BOUNDARY: Validate token with the Authorization Server
    # (RS -> AS over HTTP)
    access = await verifier.verify_token(token)
    if access is None:
        raise PermissionError("401 Unauthorized: invalid or expired token")

    if required_scopes:
        missing = [s for s in required_scopes if s not in (access.scopes or [])]
        if missing:
            raise PermissionError(f"403 Forbidden: missing scopes {missing}")


def register_tools(
    mcp: FastMCP,
    settings: ResourceServerSettings,
    verifier: TokenVerifier | None,
) -> None:
    """
    Register public and protected tools with the FastMCP server.

    Args:
        mcp: FastMCP server instance to register tools on.
        settings: RS settings that determine which tools require auth.
        verifier: Optional TokenVerifier used by protected tools.

    Tutorial note:
        We wire settings + verifier into tool closures so tools can make per-call
        decisions about whether to require authentication.
    """

    @mcp.tool(
        name="greet",
        title="Greet a user",
        description="Return a friendly greeting for the provided name.",
    )
    def greet(name: str, punctuation: str = "!") -> str:
        """
        Generate a greeting.

        Args:
            name: The name to greet.
            punctuation: Optional punctuation to use at the end of the greeting.

        Returns:
            A friendly greeting string.

        Tutorial note:
            This is a public tool; it does not require a token and is great for quick
            connectivity tests with the MCP Inspector.
        """
        safe_name = name.strip() or "there"
        end = punctuation if punctuation else "!"
        return f"Hello, {safe_name}{end}"

    @mcp.tool(
        name="server_time",
        title="Get current server time",
        description="Returns the server's current time and related details (protected).",
    )
    async def server_time(ctx: Context) -> dict[str, Any]:
        """
        Get the current server time (protected).

        This tool requires a valid Bearer token if listed in RS_REQUIRE_AUTH_FOR_TOOLS.
        The Resource Server validates the token with the Authorization Server via the
        TokenVerifier that the app layer provided.

        Returns:
            A JSON-serializable dictionary with time information.

        Raises:
            PermissionError: If authentication is required and fails.

        Tutorial note:
            This demonstrates authorization at the tool level. Instead of protecting the
            entire HTTP endpoint, we only protect this tool by calling the TokenVerifier.
        """
        # Decide if this tool requires auth based on settings
        if "server_time" in (settings.require_auth_for_tools or []):
            # Optionally require a scope; this can be customized as needed
            required_scopes = []  # e.g., ["user"]
            await _require_authenticated(ctx, verifier, required_scopes=required_scopes)

        now = datetime.datetime.now()
        return {
            "current_time": now.isoformat(),
            "timezone": "UTC",  # Simplified for demo
            "timestamp": now.timestamp(),
            "formatted": now.strftime("%Y-%m-%d %H:%M:%S"),
        }
