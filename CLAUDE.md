# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project context

This is the **reference implementation** for a multi-part developer tutorial on building MCP servers with authentication. The code serves as both:

1. A complete, working example of an MCP server with OAuth 2.1 authentication
2. The "answer key" that tutorial readers can compare their work against

See `PLAN.md` for the tutorial structure and implementation strategy.

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

### Tutorial-driven development

When implementing features, always consider:

1. **Learning progression** - Features should build on each other logically
2. **Clarity over cleverness** - Code should be immediately understandable
3. **Explicit teaching** - Use verbose variable names and extensive comments
4. **Testable milestones** - Each tutorial part must produce a working server

### Code quality rules

1. **Package management**: Use `uv` rather than `pip` in all contexts

2. **Type hints**: Required for all functions and methods

3. **Line length**: 120 characters maximum

4. **Function design**: Small, focused functions with single responsibilities

5. **Variable naming**: Use full, descriptive names (e.g., `authorization_code` not `auth_code`)

### Documentation requirements

#### File headers

Every Python file must start with a tutorial-aware docstring:

```python
"""
Part X: [Module purpose]

This module [what it does] for the MCP server demo.

Tutorial context:
- Added in Part X
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

## Running and testing

### Development server

```bash
# Run the complete implementation (Part 6)
uv run server.py

# Test with MCP Inspector
uv run mcp dev server.py

# Run tests for specific tutorial part
uv run pytest tests/test_part1.py -v
```

### Tutorial checkpoints

```bash
# Check out specific tutorial part
git checkout tutorial/part-1

# Verify the part works
uv run mcp dev server.py
```

## Implementation patterns

### From the SDK

When implementing features:

1. Check `../mcp-python-sdk/src/mcp/` for correct API usage
2. Reference `../mcp-python-sdk/examples/` for patterns
3. Use FastMCP for high-level server implementation
4. Follow OAuth patterns from `mcp/server/auth/`

### Server configuration

Use Pydantic BaseSettings with clear defaults for tutorial:

```python
class DemoSettings(BaseSettings):
    """Configuration for the MCP demo server."""
    
    model_config = SettingsConfigDict(
        env_prefix="MCP_",
        env_file=".env"
    )
    
    # Tutorial Part 1: Basic server
    server_name: str = "mcp-demo-server"
    
    # Tutorial Part 2: Auth foundation  
    auth_enabled: bool = False
    auth_mode: Literal["demo", "production"] = "demo"
    
    # Tutorial Part 3: Auth flow
    demo_username: str = "demo_user"
    demo_password: str = "demo_password"
    
    # Tutorial Part 6: Production
    token_lifetime: int = 3600
    refresh_enabled: bool = False
```

## Git workflow

### Commit messages

Follow the pattern from PLAN.md:

```
Part X: [Feature] - [What it teaches]

Examples:
Part 1: Add basic FastMCP server - Teaches MCP fundamentals
Part 3: Implement token exchange - Teaches OAuth code flow
```

### Branch strategy

- `main` - Complete Part 6 implementation
- `tutorial/part-X` - Tagged checkpoints for each tutorial part

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

## Common pitfalls to avoid

1. **Over-abstraction** - Keep code readable, even if it means some repetition
2. **Magic values** - Always explain where values come from
3. **Hidden complexity** - Make all steps explicit
4. **Assuming knowledge** - Explain OAuth concepts as they appear
5. **Incomplete examples** - Every code snippet should be runnable

## Success criteria

The implementation succeeds when:

1. Each tutorial part runs independently
2. Code is self-documenting through names and comments
3. Errors provide learning opportunities with helpful messages
4. The progression from Part 1 to Part 6 feels natural
5. Developers can understand the "why" behind each decision