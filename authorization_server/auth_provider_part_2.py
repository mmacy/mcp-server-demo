"""
Part 2 (Authorization Server): Logic layer (provider stub)

This module defines the Authorization Server (AS) provider that implements the
OAuthAuthorizationServerProvider protocol expected by the SDK. In Part 2,
we intentionally keep behavior minimal—only client registration and retrieval
are implemented—so the web layer can start serving discovery metadata and basic
endpoints while the full OAuth flow is added later.

Tutorial context:

- Added in Part 2
- Service: AS
- Layer: Logic
- Teaches: Interface-first design and progressive enhancement
- Prerequisites: Understanding of the provider protocol from the SDK

Key learning points:

- Start with a minimal, testable provider that satisfies the interface.
- Defer complex OAuth behaviors (authorize, token exchange, refresh, revoke)
  to later parts of the tutorial.
- Keep state management explicit and easy to follow (e.g., in-memory store).
"""

from __future__ import annotations

from typing import Any

from mcp.server.auth.provider import (
    AccessToken,
    AuthorizationCode,
    AuthorizationParams,
    OAuthAuthorizationServerProvider,
    RefreshToken,
)
from mcp.shared.auth import OAuthClientInformationFull, OAuthToken


class InMemoryAuthProvider(OAuthAuthorizationServerProvider[AuthorizationCode, RefreshToken, AccessToken]):
    """
    Minimal in-memory provider for Part 2.

    Implements only:
    - get_client
    - register_client

    All other methods are intentionally left unimplemented and will be added in
    subsequent parts of the tutorial (authorization flow, token issuance, etc.).
    """

    def __init__(self) -> None:
        # TUTORIAL: Keep state simple and explicit for teaching purposes.
        self._clients: dict[str, OAuthClientInformationFull] = {}

    # --- Client registration and retrieval (Part 2) ---

    async def get_client(self, client_id: str) -> OAuthClientInformationFull | None:
        """
        Retrieve a registered client by ID.

        Args:
            client_id: The client's unique identifier.

        Returns:
            The full client information if found; otherwise None.

        Tutorial note:
            This enables dynamic client registration metadata to be meaningful
            in Part 2. The rest of the protocol evolves in later parts.
        """
        return self._clients.get(client_id)

    async def register_client(self, client_info: OAuthClientInformationFull) -> None:
        """
        Register a new OAuth client.

        Args:
            client_info: The client's metadata and credentials.

        Raises:
            None (Part 2 keeps validation minimal)

        Tutorial note:
            In later parts, you will add validation and persistence.
        """
        self._clients[client_info.client_id] = client_info

    # --- OAuth flow (stubbed for Part 2) ---

    async def authorize(self, client: OAuthClientInformationFull, params: AuthorizationParams) -> str:
        """
        Begin the authorization flow.

        Part 2 stub:
            This will be fully implemented in Part 3. For now, we make the
            behavior explicit so attempts to use the flow provide a clear error.
        """
        raise NotImplementedError("Authorization flow is implemented in Part 3")

    async def load_authorization_code(
        self, client: OAuthClientInformationFull, authorization_code: str
    ) -> AuthorizationCode | None:
        """
        Load an authorization code by its value.

        Part 2 stub:
            Implemented in Part 3 when the authorization flow is added.
        """
        raise NotImplementedError("Authorization codes are handled in Part 3")

    async def exchange_authorization_code(
        self, client: OAuthClientInformationFull, authorization_code: AuthorizationCode
    ) -> OAuthToken:
        """
        Exchange an authorization code for tokens.

        Part 2 stub:
            Implemented in Part 3 alongside PKCE validation and token issuance.
        """
        raise NotImplementedError("Token exchange is implemented in Part 3")

    async def load_refresh_token(self, client: OAuthClientInformationFull, refresh_token: str) -> RefreshToken | None:
        """
        Load a refresh token by its value.

        Part 2 stub:
            Implemented in later parts when refresh support is introduced.
        """
        raise NotImplementedError("Refresh tokens are implemented in a later part")

    async def exchange_refresh_token(
        self,
        client: OAuthClientInformationFull,
        refresh_token: RefreshToken,
        scopes: list[str],
    ) -> OAuthToken:
        """
        Exchange a refresh token for a new access token (and possibly a new refresh token).

        Part 2 stub:
            Implemented in later parts when refresh support is introduced.
        """
        raise NotImplementedError("Refresh token exchange is implemented in a later part")

    async def load_access_token(self, token: str) -> AccessToken | None:
        """
        Load and validate an access token.

        Part 2 stub:
            Implemented in Part 3/4 when token issuance and validation are added.
        """
        raise NotImplementedError("Access token loading is implemented in a later part")

    async def revoke_token(self, token: AccessToken | RefreshToken) -> None:
        """
        Revoke an access or refresh token.

        Part 2 stub:
            Implemented when revocation support is introduced.
        """
        # No-op in Part 2 so revocation endpoint remains inactive unless enabled later.
        return None
