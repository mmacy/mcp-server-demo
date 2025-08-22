"""
Part 4 (Resource Server): Protect the server and refactor

This module refactors the Part 1 single-file Resource Server into a layered structure and
adds authentication integration. The Resource Server (which is also the MCP server) now:

1) Loads configuration
2) Creates a TokenVerifier that calls the Authorization Server (AS) over HTTP
3) Wires tools from the content layer (tools.py)
4) Optionally enforces auth for protected tools

Tutorial context:

- Added in Part 4
- Service: RS (Resource Server)
- Layer: App (server setup and auth integration)
- Teaches: Service boundaries, auth integration, layered structure
- Prerequisites: Part 1 server, Part 2-3 AS endpoints and flow

Key learning points:

- Keeping RS and AS physically separated and communicating only via HTTP
- Encapsulating token verification behind a TokenVerifier class
- Clean separation between app wiring (server.py) and content (tools.py)
"""

from __future__ import annotations

import logging
from typing import Any

from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

from mcp.server.auth.provider import AccessToken, TokenVerifier
from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.utilities.logging import configure_logging, get_logger
from mcp.shared._httpx_utils import create_mcp_http_client

logger = get_logger(__name__)


class ResourceServerSettings(BaseSettings):
    """Configuration for the Resource Server (MCP server)."""

    model_config = SettingsConfigDict(env_prefix="RS_", env_file=".env", extra="ignore")

    # Tutorial Part 1: Basic server
    server_name: str = "mcp-demo-resource-server"

    # Tutorial Part 4: Auth integration
    auth_enabled: bool = False
    # Base URL for the Authorization Server (e.g., http://localhost:9000)
    auth_server_url: str = "http://localhost:9000"
    # Name of tools that should require a valid token (others are public)
    require_auth_for_tools: list[str] = ["server_time"]

    # Logging
    log_level: str = "INFO"


class IntrospectionTokenVerifier(TokenVerifier):
    """
    Token verifier that calls the Authorization Server's introspection endpoint.

    TUTORIAL: This class represents the service boundary between the Resource Server (RS)
    and the Authorization Server (AS). The RS validates access tokens by making an HTTP
    call to the AS. This prevents tight coupling and keeps responsibilities cleanly split.

    Expected Authorization Server endpoint:
        POST {auth_server_url}/introspect
        form data: token=<access_token>

    A minimal introspection response shape expected by this verifier:
        {
          "active": true,
          "client_id": "client-123",
          "scope": "user read:things",
          "exp": 1735689600,
          "aud": "https://your.resource.server"  # Optional audience/resource
        }
    """

    def __init__(self, auth_server_url: str) -> None:
        self._introspection_url = auth_server_url.rstrip("/") + "/introspect"

    async def verify_token(self, token: str) -> AccessToken | None:
        """
        Verify a bearer token via Authorization Server introspection.

        Args:
            token: The opaque bearer token presented by the client.

        Returns:
            AccessToken if valid, or None if invalid.
        """
        try:
            async with create_mcp_http_client() as client:
                # SERVICE BOUNDARY: RS calling AS for token validation
                response = await client.post(self._introspection_url, data={"token": token})
                if response.status_code != 200:
                    logging.warning("Introspection call failed with status %s", response.status_code)
                    return None

                data: dict[str, Any] = response.json()
                if not data.get("active", False):
                    return None

                scopes = data.get("scope", "")
                scope_list = [s for s in scopes.split() if s] if isinstance(scopes, str) else []
                expires_at = int(data["exp"]) if "exp" in data and data["exp"] is not None else None
                audience = data.get("aud") if isinstance(data.get("aud"), str | None) else None

                # TUTORIAL: Convert introspection response to AccessToken for internal use
                return AccessToken(
                    token=token,
                    client_id=str(data.get("client_id", "")),
                    scopes=scope_list,
                    expires_at=expires_at,
                    resource=audience,
                )
        except Exception:
            logging.exception("Error during token introspection")
            return None


# Initialize settings and logging early
settings = ResourceServerSettings()
configure_logging(settings.log_level)  # Use the same rich logging as the SDK
logger.info("Starting Resource Server with name: %s", settings.server_name)

# TUTORIAL: Create the FastMCP server (MCP server) instance.
# In Part 4, we refactor tools into a separate module. We also add a TokenVerifier
# object that tools can use to validate bearer tokens (service boundary: RS -> AS).
mcp = FastMCP(
    name=settings.server_name,
    instructions=(
        "Welcome to the Part 4 Resource Server. "
        "This server demonstrates a layered structure with optional authentication."
    ),
)

# Create TokenVerifier instance if auth is enabled
token_verifier: IntrospectionTokenVerifier | None = None
if settings.auth_enabled:
    token_verifier = IntrospectionTokenVerifier(settings.auth_server_url)
    logger.info("Auth is enabled. Using Authorization Server at: %s", settings.auth_server_url)
else:
    logger.info("Auth is disabled. All tools act as public in this configuration.")

# Register tools from the content layer, passing settings and verifier
from .tools import register_tools  # noqa: E402  (import after mcp creation)

register_tools(mcp, settings, token_verifier)


if __name__ == "__main__":
    # TUTORIAL: Run the server using the default stdio transport for simplicity.
    # Try it (public-only): uv run mcp dev resource_server/server.py
    #
    # In later parts you will run this over HTTP transports and integrate with the
    # Authorization Server for full 401 behaviors and WWW-Authenticate headers.
    mcp.run()
