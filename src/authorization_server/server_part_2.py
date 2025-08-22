"""
Part 2 (Authorization Server): Web layer (server setup and routes)

This module creates the Authorization Server (AS) web application and exposes the
OAuth 2.1 discovery and core endpoints. In Part 2, the logic layer is intentionally
stubbed, and the focus is on establishing a clean two-file structure (web/logic)
and serving the well-known metadata endpoint.

Tutorial context:

- Added in Part 2
- Service: AS
- Layer: Web
- Teaches: Service separation, clean architecture, OAuth metadata endpoint
- Prerequisites: Part 1 basic resource server understanding

Key learning points:

- Keep service boundaries clear: the web layer wires HTTP endpoints, while the
  logic layer implements OAuth behavior behind a clean interface.
- Expose OAuth 2.0 Authorization Server Metadata at
  /.well-known/oauth-authorization-server so clients can discover endpoints.
- Use simple, descriptive settings and strong types to make configuration obvious.
"""

import logging

from auth_provider import InMemoryAuthProvider
from mcp.server.auth.routes import create_auth_routes
from mcp.server.auth.settings import ClientRegistrationOptions
from pydantic import AnyHttpUrl, BaseModel
from starlette.applications import Starlette
from uvicorn import Config, Server


class AuthServerSettings(BaseModel):
    """Settings for the Authorization Server (AS)."""

    # Tutorial Part 2: AS foundation
    server_port: int = 9000
    issuer: AnyHttpUrl = AnyHttpUrl("http://localhost:9000")


def create_app(settings: AuthServerSettings | None = None) -> Starlette:
    """
    Create and configure the Starlette application for the Authorization Server.

    Args:
        settings: Optional AuthServerSettings to configure the server. If not provided,
            sensible defaults are used for local development.

    Returns:
        A configured Starlette application exposing OAuth 2.1 endpoints.

    Tutorial note:
        This function demonstrates the separation of concerns: we construct the
        web layer here and delegate all OAuth logic to the provider instance
        (defined in auth_provider.py). In Part 2, most provider methods are stubs.
    """
    logging.getLogger("uvicorn.error").setLevel(logging.INFO)

    # Use defaults if no settings provided
    settings = settings or AuthServerSettings()

    # TUTORIAL: The provider implements the OAuthAuthorizationServerProvider protocol.
    # In Part 2, it's only partially implemented (get_client/register_client).
    provider = InMemoryAuthProvider()

    # TUTORIAL: Build routes using the SDK helper so the server is spec-compliant.
    # We enable dynamic client registration here to showcase the full metadata shape.
    routes = create_auth_routes(
        provider=provider,
        issuer_url=settings.issuer,
        service_documentation_url=None,
        client_registration_options=ClientRegistrationOptions(enabled=True),
        revocation_options=None,
    )

    # Return the Starlette app with OAuth routes registered
    return Starlette(routes=routes)


def main() -> int:
    """
    Run the Authorization Server with Uvicorn.

    Returns:
        Process exit code (0 for success)

    Tutorial note:
        You can run this server with:
            uv run authorization_server/server.py
        Then visit:
            http://localhost:9000/.well-known/oauth-authorization-server
        to verify the metadata endpoint is working.
    """
    app = create_app()
    settings = AuthServerSettings()

    config = Config(
        app,
        host="127.0.0.1",
        port=settings.server_port,
        log_level="info",
    )
    server = Server(config)
    server.run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
