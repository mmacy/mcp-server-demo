# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project context

This is the **reference implementation** for a multi-part developer tutorial on building MCP servers with authentication. The code demonstrates a **two-service architecture** that physically separates:

1. **Resource Server (RS)** - The MCP server that provides tools and resources
2. **Authorization Server (AS)** - The OAuth 2.1 server that handles authentication

The implementation serves as both:
- A complete, working example of secure MCP server architecture
- The "answer key" that tutorial readers can compare their work against

See `PLAN.md` for the detailed tutorial structure and implementation strategy.

## Audience

Experienced MCP server developers who are:

- Proficient in Python
- New to OAuth 2.1 and authorization in MCP servers
- Following the tutorial to learn authentication patterns

## Important references

### MCP Python SDK

The MCP Python SDK is available locally at `../mcp-python-sdk/` and its source code in `../mcp-python-sdk/src/mcp` should be used as the authoritative reference during implementation. Always check the SDK source code for correct API usage, not just the documentation.

### Authorization specification

The Authorization section of the MCP protocol specification is available in `mcp-specification-202506-18-authorization.md`. Refer to this specification for standards compliance and implementation requirements.

## Development guidelines

### Service architecture principles

1. **Physical separation** - RS and AS are separate services in separate directories
2. **Clear boundaries** - Services communicate only through HTTP APIs
3. **Layered structure**:
   - **AS**: `server.py` (web layer) + `auth_provider.py` (logic layer)
   - **RS**: `server.py` (app layer) + `tools.py` (content layer, added Part 4)
4. **Progressive complexity** - Start simple (single file), refactor to structured

### Tutorial-driven development

When implementing features, always consider:

1. **Learning progression** - Start with a single-file RS, then build the AS, then integrate
2. **Service boundaries** - Maintain clear separation between RS and AS
3. **Clarity over cleverness** - Code should be immediately understandable
4. **Explicit teaching** - Use verbose variable names and extensive comments
5. **Progressive refactoring** - Show evolution from simple to well-structured
6. **Testable milestones** - Each tutorial part must produce working, runnable services

### Code quality rules

1. **Package management**: Use `uv` rather than `pip` in all contexts

2. **Type hints**: Required for all functions and methods

3. **Line length**: 120 characters maximum

4. **Function design**: Small, focused functions with single responsibilities

5. **Variable naming**: Use full, descriptive names (e.g., `authorization_code` not `auth_code`)

### Documentation requirements

#### File headers

Every Python file must start with a tutorial-aware docstring that includes service context:

```python
"""
Part X (Service): [Module purpose]

This module [what it does] for the [Resource Server/Authorization Server].

Tutorial context:

- Added in Part X
- Service: [RS/AS]
- Layer: [Web/Logic/App/Content]
- Teaches: [key concepts]
- Prerequisites: [what must be understood first]

Key learning points:

- [Concept 1]
- [Concept 2]
"""
```

#### Function docstrings

Follow Google Python Style Guide with tutorial context:

```python
async def exchange_authorization_code(
    self,
    code: str,
    verifier: str
) -> OAuthToken:
    """
    Exchange an authorization code for access tokens.

    This is Part 3 of the OAuth flow where the client proves it
    initiated the request by providing the PKCE verifier.

    Args:
        code: The authorization code from the auth server
        verifier: The PKCE code_verifier that matches the original challenge

    Returns:
        OAuth token containing access_token and optional refresh_token

    Raises:
        TokenError: If the code is invalid or expired

    Tutorial note:
        This demonstrates PKCE validation, a critical security measure
        that prevents authorization code interception attacks.
    """
```

#### Inline comments

Use comments to teach, not just describe:

```python
# TUTORIAL: We validate the PKCE verifier by hashing it and comparing
# to the stored challenge. This proves the client that's exchanging
# the code is the same one that initiated the auth request.
challenge = base64.urlsafe_b64encode(
    hashlib.sha256(verifier.encode()).digest()
).rstrip(b'=').decode('ascii')

if challenge != stored_challenge:
    # SECURITY: This is a critical check - without it, anyone who
    # intercepts the authorization code could exchange it for tokens
    raise TokenError("invalid_grant", "PKCE verification failed")
```

#### Service interaction comments

When services interact, explain the flow:

```python
# TUTORIAL: The RS needs to verify tokens with the AS.
# This HTTP call represents the service-to-service communication
# that validates the client's access token.
async def verify_token(self, token: str) -> bool:
    """Verify a token with the Authorization Server."""
    # SERVICE BOUNDARY: RS calling AS for token validation
    response = await self.http_client.post(
        f"{self.auth_server_url}/token/introspect",
        data={"token": token}
    )
    # The AS returns token metadata if valid
    return response.json().get("active", False)
```

## Running and testing

### Development servers

```bash
# Run the Resource Server (MCP server)
uv run resource_server/server.py

# Run the Authorization Server (in separate terminal)
uv run authorization_server/server.py

# Test RS with MCP Inspector
uv run mcp dev resource_server/server.py

# Test the client (both servers must be running)
uv run client.py

# Run tests for specific tutorial part
uv run pytest tests/test_part1.py -v
```

### Tutorial checkpoints

```bash
# Check out specific tutorial part
git checkout tutorial/part-1

# Verify the RS works (Part 1+)
uv run mcp dev resource_server/server.py

# Verify the AS works (Part 2+)
uv run authorization_server/server.py

# Test full integration (Part 4+)
# Terminal 1: uv run authorization_server/server.py
# Terminal 2: uv run resource_server/server.py
# Terminal 3: uv run client.py
```

## Implementation patterns

### From the SDK

When implementing features:

1. Check `../mcp-python-sdk/src/mcp/` for correct API usage
2. Reference `../mcp-python-sdk/examples/` for patterns
3. Use FastMCP for the Resource Server (MCP server) implementation
4. Follow OAuth patterns from `mcp/server/auth/` for RS token verification
5. Build the Authorization Server as a separate FastAPI application

### Service configuration

Each service has its own configuration:

#### Resource Server (RS)
```python
class ResourceServerSettings(BaseSettings):
    """Configuration for the Resource Server (MCP server)."""

    model_config = SettingsConfigDict(
        env_prefix="RS_",
        env_file=".env"
    )

    # Tutorial Part 1: Basic server
    server_name: str = "mcp-demo-resource-server"

    # Tutorial Part 4: Auth integration
    auth_enabled: bool = False
    auth_server_url: str = "http://localhost:9000"
    require_auth_for_tools: list[str] = []
```

#### Authorization Server (AS)
```python
class AuthServerSettings(BaseSettings):
    """Configuration for the Authorization Server."""

    model_config = SettingsConfigDict(
        env_prefix="AS_",
        env_file=".env"
    )

    # Tutorial Part 2: AS foundation
    server_port: int = 9000
    issuer: str = "http://localhost:9000"

    # Tutorial Part 3: Auth flow
    demo_username: str = "demo_user"
    demo_password: str = "demo_password"

    # Tutorial Part 6: Enhanced features
    token_lifetime: int = 3600
    refresh_enabled: bool = False
```

## Git workflow

### Commit messages

Follow the pattern from PLAN.md, including service specification:

```
Part X (Service): [Feature] - [What it teaches]

Examples:
Part 1 (RS): Add basic FastMCP server - Teaches MCP fundamentals
Part 2 (AS): Create web and logic layers - Teaches separation of concerns
Part 3 (AS): Implement token exchange - Teaches OAuth code flow
Part 4 (RS): Add token verifier - Teaches service-to-service validation
Part 5: Add client example - Teaches three-party OAuth flow
Part 6 (RS+AS): Add enhanced patterns - Teaches advanced concepts
```

### Branch strategy

- `main` - Complete implementation with all 6 parts
- `tutorial/part-X` - Tagged checkpoints for each tutorial part

### Development workflow

1. Build Part 1 first (single-file RS)
2. Layer on each subsequent part
3. Test at each checkpoint
4. Tag stable states for tutorial reference

## Testing philosophy

Tests serve as both validation and documentation:

```python
def test_public_tool_without_auth():
    """
    Part 1: Verify public tools work without authentication.

    This test demonstrates that tools can be accessed
    without any authentication when auth is disabled.
    """
    # Test implementation that teaches
```

### Service-specific testing

```python
# tests/test_resource_server.py
def test_rs_token_verification():
    """
    Part 4: Test RS verification of tokens with AS.

    Shows the service boundary: RS calls AS to validate tokens.
    """
    pass

# tests/test_auth_server.py
def test_as_token_generation():
    """
    Part 3: Test AS OAuth flow and token generation.

    Demonstrates AS operating independently as auth provider.
    """
    pass
```

## Common pitfalls to avoid

1. **Over-abstraction** - Keep code readable, even if it means some repetition
2. **Magic values** - Always explain where values come from
3. **Hidden complexity** - Make all steps explicit
4. **Assuming knowledge** - Explain OAuth concepts as they appear
5. **Incomplete examples** - Every code snippet should be runnable
6. **Mixing concerns** - Keep RS and AS logic strictly separated
7. **Premature structure** - Don't introduce `tools.py` until Part 4
8. **Service coupling** - Services should only interact via HTTP, never share code

## File structure

The project uses a two-service architecture with clear separation:

```
mcp-server-demo/
├── authorization_server/
│   ├── __init__.py
│   ├── server.py         # AS web layer: routes and server setup
│   └── auth_provider.py  # AS logic layer: core OAuth implementation
├── resource_server/
│   ├── __init__.py
│   ├── server.py         # RS app layer: server setup and auth protection
│   └── tools.py          # RS content layer: MCP tool definitions (Part 4+)
├── client.py             # Example client to test the full flow (Part 5+)
├── tests/
│   ├── test_resource_server.py
│   └── test_auth_server.py
├── .env.example
├── pyproject.toml
└── README.md
```

## Tutorial progression

### Part 1: Basic resource server

- Create `resource_server/server.py` with a single public tool
- Run with `uv run mcp dev resource_server/server.py`
- Teaches: MCP fundamentals, FastMCP basics

### Part 2: Authorization server foundation

- Create `authorization_server/` with two-file structure
- `server.py`: Web layer with routes
- `auth_provider.py`: Logic layer (initially stubbed)
- Teaches: Service separation, clean architecture

### Part 3: Complete AS implementation

- Implement full OAuth flow in `auth_provider.py`
- Wire up login form, authorization, and token endpoints
- Teaches: OAuth 2.1 flow, PKCE, token generation

### Part 4: Protect RS and refactor

- Add `TokenVerifier` class to RS
- Extract tools to `resource_server/tools.py`
- Add protected tools requiring authentication
- Teaches: Service integration, token validation, refactoring

### Part 5: Client implementation

- Create `client.py` for full three-party flow
- Demonstrates complete authentication flow
- Teaches: Client-side OAuth, MCP client patterns

### Part 6: Enhanced patterns

- Add database persistence to AS
- Implement token scopes in RS
- Add configuration management
- Teaches: Advanced patterns, additional security layers

## Service interaction patterns

### Resource Server (RS)

- The RS **is** the MCP server that provides tools
- Starts as a single file in Part 1
- Refactored to two-file structure in Part 4
- Validates tokens by calling AS endpoints

### Authorization Server (AS)

- Separate FastAPI application on port 9000
- Two-file structure from the start (Part 2)
- Provides OAuth 2.1 endpoints and token validation

### Key teaching moments

1. **Part 1**: Single service, no auth - baseline functionality
2. **Part 2-3**: Build AS separately - understand OAuth in isolation
3. **Part 4**: Connect services - see how they interact
4. **Part 5**: Add client - complete the three-party OAuth dance
5. **Part 6**: Enhanced features - demonstrate advanced concepts

## Success criteria

The implementation succeeds when:

1. Each tutorial part runs independently and produces working services
2. Service boundaries are clear and well-defined
3. The evolution from single-file to multi-file structure is logical
4. Code is self-documenting through names and comments
5. Errors provide learning opportunities with helpful messages
6. The progression from Part 1 to Part 6 feels natural
7. Developers understand both the "what" and "why" of the architecture

## Markdown formatting guidelines

- You MUST surround lists, headings, and fenced code blocks with blank lines; this applies to lists that appear within lists.
- You MUST use sentence case for all headings and heading-like text.
