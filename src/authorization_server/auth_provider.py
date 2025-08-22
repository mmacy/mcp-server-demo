"""
Part 3 (Authorization Server): Complete OAuth flow (logic layer)

This module implements the core OAuth logic for the Authorization Server (AS)
using an in-memory provider that conforms to the OAuthAuthorizationServerProvider
protocol from the MCP SDK.

In Part 3, we complete the OAuth flow for:
- Authorization endpoint (with PKCE challenge storage)
- Simple login UI and callback (demo credentials)
- Authorization code issuance and storage
- Token exchange (authorization_code grant) that returns access tokens
- In-memory token storage suitable for later introspection by the RS

Tutorial context:

- Added in Part 3
- Service: AS
- Layer: Logic
- Teaches: OAuth 2.1 authorization code flow, PKCE, token generation
- Prerequisites: Part 2 provider stubs and metadata endpoints

Key learning points:

- Store and validate PKCE code_challenge with authorization codes
- Issue access tokens with explicit expiration
- Keep the provider focused on logic; the web layer handles HTTP concerns
"""

import secrets
import time
from typing import Any

from pydantic import AnyHttpUrl
from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette.responses import HTMLResponse, RedirectResponse, Response

from mcp.server.auth.provider import (
    AccessToken,
    AuthorizationCode,
    AuthorizationParams,
    OAuthAuthorizationServerProvider,
    RefreshToken,
    construct_redirect_uri,
)
from mcp.shared.auth import OAuthClientInformationFull, OAuthToken


class InMemoryAuthProvider(OAuthAuthorizationServerProvider[AuthorizationCode, RefreshToken, AccessToken]):
    """
    In-memory OAuth provider implementing the authorization code flow with PKCE.

    This provider supports:
    - Dynamic client registration (stored in memory)
    - Authorization endpoint that redirects to a login form
    - Simple demo login backed by username/password
    - Authorization code issuance with PKCE code_challenge
    - Token exchange (authorization_code grant) issuing access tokens

    Note:
        This implementation is for tutorial/demo purposes and stores all state
        in memory. It is not suitable for production.
    """

    def __init__(
        self,
        *,
        issuer_url: AnyHttpUrl,
        demo_username: str = "demo_user",
        demo_password: str = "demo_password",
        token_lifetime_seconds: int = 3600,
    ) -> None:
        # In-memory stores
        self._clients: dict[str, OAuthClientInformationFull] = {}
        self._auth_codes: dict[str, AuthorizationCode] = {}
        self._access_tokens: dict[str, AccessToken] = {}

        # Track state from /authorize to login flow
        # state -> {redirect_uri, code_challenge, redirect_uri_provided_explicitly, client_id, resource}
        self._state_map: dict[str, dict[str, str | None]] = {}

        # Demo credentials and token settings
        self._demo_username = demo_username
        self._demo_password = demo_password
        self._token_lifetime_seconds = token_lifetime_seconds

        # Build login and callback URLs based on issuer URL
        base = str(issuer_url).rstrip("/")
        self._login_url = f"{base}/login"
        self._login_callback_url = f"{base}/login/callback"

    # ---------------------------
    # Client registration support
    # ---------------------------

    async def get_client(self, client_id: str) -> OAuthClientInformationFull | None:
        """
        Retrieve a registered client by ID.

        Args:
            client_id: The client's unique identifier.

        Returns:
            The full client information if found; otherwise None.
        """
        return self._clients.get(client_id)

    async def register_client(self, client_info: OAuthClientInformationFull) -> None:
        """
        Register a new OAuth client (dynamic client registration).

        Args:
            client_info: The client's metadata and credentials.

        Tutorial note:
            Validation and persistence are intentionally minimal for the tutorial.
        """
        self._clients[client_info.client_id] = client_info

    # ---------------------------
    # Authorization endpoint flow
    # ---------------------------

    async def authorize(self, client: OAuthClientInformationFull, params: AuthorizationParams) -> str:
        """
        Begin the authorization flow.

        Stores the PKCE code_challenge, redirect_uri selection, and other details
        under the provided state, then returns the login URL to display a login UI.

        Args:
            client: The client requesting authorization.
            params: Authorization request parameters including PKCE challenge.

        Returns:
            URL to redirect the user-agent to (the login form in this demo).

        Raises:
            HTTPException: If required parameters are missing or invalid.
        """
        state = params.state or secrets.token_urlsafe(16)

        # Persist state for use by the login callback
        self._state_map[state] = {
            "redirect_uri": str(params.redirect_uri),
            "code_challenge": params.code_challenge,
            "redirect_uri_provided_explicitly": str(params.redirect_uri_provided_explicitly),
            "client_id": client.client_id,
            "resource": params.resource,  # RFC 8707 resource indicator (audience)
        }

        # Redirect to our simple login page
        return f"{self._login_url}?state={state}&client_id={client.client_id}"

    # ---------------------------
    # Simple demo login UI support
    # ---------------------------

    async def get_login_page(self, state: str) -> HTMLResponse:
        """
        Render a simple login page for the demo.

        Args:
            state: The OAuth state token linking this UI to the original /authorize request.

        Returns:
            HTMLResponse containing a minimal login form.
        """
        if not state or state not in self._state_map:
            raise HTTPException(400, "Invalid or missing state parameter")

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>MCP Demo Login</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px auto; max-width: 520px; }}
                .box {{ border: 1px solid #e5e7eb; border-radius: 8px; padding: 24px; }}
                h2 {{ margin-top: 0; }}
                .row {{ margin-bottom: 12px; }}
                label {{ display: block; margin-bottom: 6px; color: #374151; }}
                input {{ width: 100%; padding: 10px; border: 1px solid #d1d5db; border-radius: 6px; }}
                button {{ margin-top: 6px; background: #2563eb; color: white; padding: 10px 16px; border: 0; border-radius: 6px; cursor: pointer; }}
                button:hover {{ background: #1d4ed8; }}
                .hint {{ color: #6b7280; font-size: 14px; margin-top: 6px; }}
                .creds {{ background: #f3f4f6; border-radius: 6px; padding: 10px; font-size: 14px; }}
            </style>
        </head>
        <body>
            <div class="box">
                <h2>MCP Demo Authentication</h2>
                <p class="hint">Use the demo credentials below to sign in:</p>
                <div class="creds">
                    <div><strong>Username:</strong> {self._demo_username}</div>
                    <div><strong>Password:</strong> {self._demo_password}</div>
                </div>

                <form action="{self._login_callback_url}" method="post">
                    <input type="hidden" name="state" value="{state}">
                    <div class="row">
                        <label>Username</label>
                        <input name="username" value="{self._demo_username}" required />
                    </div>
                    <div class="row">
                        <label>Password</label>
                        <input type="password" name="password" value="{self._demo_password}" required />
                    </div>
                    <button type="submit">Sign in</button>
                </form>
            </div>
        </body>
        </html>
        """
        return HTMLResponse(html)

    async def handle_login_callback(self, request: Request) -> Response:
        """
        Handle login form submission and redirect back to the client's redirect_uri.

        The callback validates demo credentials, generates an authorization code,
        and redirects with ?code=...&state=... appended to the original redirect_uri.

        Returns:
            RedirectResponse to the client's redirect_uri with authorization code.
        """
        form = await request.form()
        username = form.get("username")
        password = form.get("password")
        state = form.get("state")

        if not isinstance(username, str) or not isinstance(password, str) or not isinstance(state, str):
            raise HTTPException(400, "Invalid form parameters")

        if state not in self._state_map:
            raise HTTPException(400, "Unknown or expired state")

        if username != self._demo_username or password != self._demo_password:
            raise HTTPException(401, "Invalid credentials")

        state_data = self._state_map[state]
        redirect_uri = state_data["redirect_uri"]
        code_challenge = state_data["code_challenge"]
        redirect_uri_provided_explicitly = state_data["redirect_uri_provided_explicitly"] == "True"
        client_id = state_data["client_id"]
        resource = state_data.get("resource")

        assert redirect_uri is not None
        assert code_challenge is not None
        assert client_id is not None

        # Build and store authorization code (expires in 5 minutes)
        code_value = f"mcp_{secrets.token_hex(16)}"
        auth_code = AuthorizationCode(
            code=code_value,
            client_id=client_id,
            scopes=[],  # scopes are validated at registration/metadata time
            expires_at=time.time() + 300,
            code_challenge=code_challenge,
            redirect_uri=AnyHttpUrl(redirect_uri),
            redirect_uri_provided_explicitly=redirect_uri_provided_explicitly,
            resource=resource,
        )
        self._auth_codes[code_value] = auth_code

        # Clean up used state
        del self._state_map[state]

        # Redirect back to the client's redirect_uri with code and state
        return RedirectResponse(url=construct_redirect_uri(redirect_uri, code=code_value, state=state), status_code=302)

    # ---------------------------
    # Token issuance and storage
    # ---------------------------

    async def load_authorization_code(
        self, client: OAuthClientInformationFull, authorization_code: str
    ) -> AuthorizationCode | None:
        """
        Load an authorization code by its string value.

        Args:
            client: The client requesting to exchange the code.
            authorization_code: The authorization code string.

        Returns:
            The stored AuthorizationCode or None if not found.
        """
        return self._auth_codes.get(authorization_code)

    async def exchange_authorization_code(
        self, client: OAuthClientInformationFull, authorization_code: AuthorizationCode
    ) -> OAuthToken:
        """
        Exchange an authorization code for an access token.

        PKCE verification is performed by the HTTP handler (TokenHandler) using
        the stored code_challenge. This method assumes that validation has passed
        and issues a new access token.

        Args:
            client: The client exchanging the authorization code.
            authorization_code: The validated authorization code object.

        Returns:
            OAuthToken containing an access token, token_type, expires_in, and scope.
        """
        # Ensure the code exists and belongs to the client
        stored = self._auth_codes.get(authorization_code.code)
        if stored is None or stored.client_id != client.client_id:
            raise HTTPException(400, "Invalid authorization code")

        # Expire the authorization code immediately after use
        del self._auth_codes[authorization_code.code]

        # Issue access token
        token_value = f"mcp_{secrets.token_hex(32)}"
        expires_at = int(time.time()) + self._token_lifetime_seconds

        access = AccessToken(
            token=token_value,
            client_id=client.client_id,
            scopes=authorization_code.scopes,
            expires_at=expires_at,
            resource=authorization_code.resource,  # RFC 8707 audience/resource binding
        )
        self._access_tokens[token_value] = access

        return OAuthToken(
            access_token=token_value,
            token_type="Bearer",
            expires_in=self._token_lifetime_seconds,
            scope=" ".join(authorization_code.scopes) if authorization_code.scopes else None,
            refresh_token=None,  # Refresh not implemented in Part 3
        )

    async def load_refresh_token(self, client: OAuthClientInformationFull, refresh_token: str) -> RefreshToken | None:
        """
        Refresh tokens are not implemented in Part 3.

        Returns:
            Always None in this implementation.
        """
        return None

    async def exchange_refresh_token(
        self,
        client: OAuthClientInformationFull,
        refresh_token: RefreshToken,
        scopes: list[str],
    ) -> OAuthToken:
        """
        Exchange a refresh token for a new access token.

        Part 3 intentionally does not implement refresh token rotation to keep the
        flow simple and focused on authorization_code + PKCE.
        """
        raise HTTPException(400, "Refresh tokens are not supported in this demo")

    async def load_access_token(self, token: str) -> AccessToken | None:
        """
        Load an access token for verification.

        Args:
            token: The bearer token string.

        Returns:
            AccessToken if valid and not expired, otherwise None.
        """
        access = self._access_tokens.get(token)
        if not access:
            return None

        if access.expires_at and access.expires_at < int(time.time()):
            # Clean up expired token
            try:
                del self._access_tokens[token]
            except KeyError:
                pass
            return None

        return access

    async def revoke_token(self, token: AccessToken | RefreshToken) -> None:
        """
        Revoke a token.

        Args:
            token: The token object to revoke.

        Behavior:
            If the token exists in storage, it is removed. No error is raised if
            the token is not found.
        """
        # Access token revocation
        if isinstance(token, AccessToken):
            try:
                del self._access_tokens[token.token]
            except KeyError:
                pass
        # Refresh tokens are not implemented in Part 3, so nothing else to do.
        return None
