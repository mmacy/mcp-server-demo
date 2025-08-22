"""
Part 3 (Authorization Server): Web layer (routes + login UI)

This module wires the Authorization Server (AS) web application, exposing the
OAuth 2.1 discovery and core endpoints, and adds a simple login UI to complete
the Authorization Code + PKCE flow.

Tutorial context:

- Updated in Part 3
- Service: AS
- Layer: Web
- Teaches: Wiring HTTP routes to provider logic, serving a login UI, and completing
  the authorization flow

Key learning points:

- Keep service boundaries clear: the web layer wires HTTP endpoints, while the
  logic layer implements OAuth behavior behind a clean interface.
- Expose OAuth 2.0 Authorization Server Metadata at
  /.well-known/oauth-authorization-server for client discovery.
- Add login and callback routes to drive the demo authentication flow.
"""

import logging

from auth_provider import InMemoryAuthProvider
from mcp.server.auth.routes import create_auth_routes
from mcp.server.auth.settings import ClientRegistrationOptions
from pydantic import AnyHttpUrl, BaseModel
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.routing import Route
from uvicorn import Config, Server


class AuthServerSettings(BaseModel):
    """Settings for the Authorization Server (AS)."""

    # Tutorial Part 2: AS foundation
    server_port: int = 9000
    issuer: AnyHttpUrl = AnyHttpUrl("http://localhost:9000")

    # Tutorial Part 3: Demo credentials and token settings
    demo_username: str = "demo_user"
    demo_password: str = "demo_password"
    token_lifetime: int = 3600


def create_app(settings: AuthServerSettings | None = None) -> Starlette:
    """
    Create and configure the Starlette application for the Authorization Server.

    Args:
        settings: Optional AuthServerSettings to configure the server. If not provided,
            sensible defaults are used for local development.

    Returns:
        A configured Starlette application exposing OAuth 2.1 endpoints and login UI.
    """
    logging.getLogger("uvicorn.error").setLevel(logging.INFO)
    settings = settings or AuthServerSettings()

    # Logic provider implementing OAuth 2.1 flows
    provider = InMemoryAuthProvider(
        issuer_url=settings.issuer,
        demo_username=settings.demo_username,
        demo_password=settings.demo_password,
        token_lifetime_seconds=settings.token_lifetime,
    )

    # Core OAuth routes (metadata, /authorize, /token, and dynamic client registration)
    routes = create_auth_routes(
        provider=provider,
        issuer_url=settings.issuer,
        service_documentation_url=None,
        client_registration_options=ClientRegistrationOptions(enabled=True),
        revocation_options=None,
    )

    # Demo login page (GET)
    async def login_page(request: Request) -> Response:
        """Render a minimal login page tied to the OAuth state."""
        state = request.query_params.get("state")
        if not isinstance(state, str) or not state:
            # Handlers will return RFC-compliant error responses on /authorize,
            # but the login page needs a basic error here for bad input.
            from starlette.exceptions import HTTPException

            raise HTTPException(400, "Missing state parameter")
        return await provider.get_login_page(state)

    # Demo login callback (POST)
    async def login_callback(request: Request) -> Response:
        """Handle login form submission and redirect back to client's redirect_uri."""
        return await provider.handle_login_callback(request)

    # Token introspection endpoint (POST)
    async def introspect(request: Request) -> Response:
        """
        Handle token introspection requests from Resource Servers.
        
        This endpoint allows the RS to validate access tokens.
        """
        form = await request.form()
        token = form.get("token")
        
        if not token or not isinstance(token, str):
            return JSONResponse({"active": False})
        
        # Validate the token with our provider
        token_info = provider.validate_access_token(token)
        
        if token_info is None:
            return JSONResponse({"active": False})
        
        # Return introspection response
        import time
        return JSONResponse({
            "active": True,
            "client_id": token_info.get("client_id", ""),
            "scope": " ".join(token_info.get("scopes", [])),
            "exp": token_info.get("expires_at"),
            "iat": int(time.time()),  # Issued at
        })

    # Add login and introspection routes
    routes.extend(
        [
            Route("/login", endpoint=login_page, methods=["GET"]),
            Route("/login/callback", endpoint=login_callback, methods=["POST"]),
            Route("/introspect", endpoint=introspect, methods=["POST"]),
        ]
    )

    return Starlette(routes=routes)


def main() -> int:
    """
    Run the Authorization Server with Uvicorn.

    Returns:
        Process exit code (0 for success)

    How to run:
        uv run authorization_server/server.py
    Verify metadata:
        http://localhost:9000/.well-known/oauth-authorization-server
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
