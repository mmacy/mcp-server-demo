# MCP server demo - implementation plan

## Project goals

Build a comprehensive MCP server with authentication that serves as an educational example for developers new to authorization in MCP servers. The implementation should be clear enough for quick understanding but complex enough to demonstrate real-world patterns.

## Architecture overview

### Core components

1. **MCP server (resource server)**

   - Built with FastMCP for clean, high-level API
   - Acts as OAuth 2.1 resource server
   - Provides protected tools and resources
   - Implements OAuth 2.0 Protected Resource Metadata (RFC 9728)

2. **Authorization server**

   - OAuth 2.1 compliant implementation
   - Supports Dynamic Client Registration (RFC 7591)
   - Provides Authorization Server Metadata (RFC 8414)
   - Token management (access tokens, refresh tokens)

3. **Authentication provider**

   - Configurable authentication backend
   - Demo mode with hardcoded credentials
   - Production-ready patterns for real authentication

## Implementation phases

### Phase 1: Foundation setup

#### 1.1 Project structure

```
mcp-server-demo/
├── server.py                 # Main MCP server entry point
├── auth/
│   ├── __init__.py
│   ├── provider.py          # OAuth provider interface
│   ├── demo_provider.py     # Demo auth provider
│   ├── token_manager.py     # Token storage and validation
│   └── middleware.py        # Bearer token middleware
├── resources/
│   ├── __init__.py
│   ├── public.py           # Public resources (no auth)
│   └── protected.py        # Protected resources
├── tools/
│   ├── __init__.py
│   ├── public.py           # Public tools
│   └── protected.py        # Protected tools
├── config.py               # Configuration management
├── .env.example            # Environment variables template
└── tests/
    ├── test_auth.py
    ├── test_server.py
    └── test_integration.py
```

#### 1.2 Dependencies and configuration

- Set up `pyproject.toml` with all required dependencies
- Create `.env.example` with clear documentation
- Implement Pydantic settings for configuration

### Phase 2: Authentication infrastructure

#### 2.1 OAuth provider implementation

- Create abstract `OAuthProvider` base class
- Implement `DemoAuthProvider` with:
  - Hardcoded demo credentials
  - Simple login form
  - Token generation and validation
  - Session management

#### 2.2 Token management

- Implement token storage (in-memory for demo)
- Token validation and expiration
- Refresh token support
- Token revocation

#### 2.3 Authorization server endpoints

- `/.well-known/oauth-authorization-server` - Server metadata
- `/register` - Dynamic client registration
- `/authorize` - Authorization endpoint
- `/token` - Token endpoint
- `/revoke` - Token revocation
- `/login` - Simple login form (demo mode)

### Phase 3: MCP server implementation

#### 3.1 FastMCP server setup

- Initialize FastMCP with proper configuration
- Configure transport (Streamable HTTP)
- Set up logging and debugging

#### 3.2 Protected resource metadata

- Implement `/.well-known/oauth-protected-resource`
- Return proper authorization server URLs
- Handle `WWW-Authenticate` headers

#### 3.3 Bearer token middleware

- Validate bearer tokens in Authorization header
- Extract token claims and user context
- Handle 401 Unauthorized responses

### Phase 4: MCP features

#### 4.1 Public features (no auth required)

```python
# Public tool example
@server.tool(auth_required=False)
async def get_time():
    """Get current server time."""
    return datetime.now().isoformat()

# Public resource example
@server.resource(auth_required=False)
async def readme():
    """Server documentation."""
    return "MCP Server Demo README"
```

#### 4.2 Protected features (auth required)

```python
# Protected tool example
@server.tool(auth_required=True)
async def get_user_data(context: AuthContext):
    """Get authenticated user's data."""
    return {
        "user_id": context.user_id,
        "username": context.username,
        "scopes": context.scopes
    }

# Protected resource example
@server.resource(auth_required=True)
async def user_profile(context: AuthContext):
    """User's private profile."""
    return f"Profile for {context.username}"
```

#### 4.3 Scope-based access control

```python
# Tool requiring specific scope
@server.tool(auth_required=True, required_scopes=["admin"])
async def admin_action(context: AuthContext):
    """Perform administrative action."""
    return "Admin action completed"
```

### Phase 5: Client examples

#### 5.1 Simple test client

- Demonstrate authorization flow
- Handle token refresh
- Show scope-based access

#### 5.2 Interactive demo script

- Guide users through auth flow
- Display clear status messages
- Handle errors gracefully

### Phase 6: Documentation and testing

#### 6.1 Documentation

- Comprehensive docstrings following Google Python Style Guide
- Clear README with setup instructions
- Architecture documentation with diagrams
- Step-by-step authorization flow explanation

#### 6.2 Testing

- Unit tests for auth components
- Integration tests for full auth flow
- MCP protocol compliance tests
- Error handling tests

## Key implementation details

### Security considerations

1. **PKCE implementation**
   - Always use code_challenge/code_verifier
   - SHA256 hashing for code challenge

2. **Token security**
   - Short-lived access tokens (1 hour)
   - Longer refresh tokens (30 days)
   - Secure token generation (secrets.token_urlsafe)

3. **HTTPS requirements**
   - Enforce HTTPS in production
   - Allow HTTP for local development only

### Educational features

1. **Clear code structure**
   - Separate concerns clearly
   - Use descriptive variable names
   - Add explanatory comments

2. **Progressive complexity**
   - Start with basic auth flow
   - Add advanced features incrementally
   - Provide configuration toggles

3. **Error messages**
   - Detailed, helpful error messages
   - Include suggestions for fixes
   - Link to relevant documentation

### Configuration options

```ini
# .env configuration
FASTMCP_DEBUG=true
FASTMCP_LOG_LEVEL=DEBUG

# Auth configuration
MCP_AUTH_MODE=demo  # or "production"
MCP_AUTH_DEMO_USERNAME=demo_user
MCP_AUTH_DEMO_PASSWORD=demo_password

# Token configuration
MCP_ACCESS_TOKEN_LIFETIME=3600
MCP_REFRESH_TOKEN_LIFETIME=2592000

# Server URLs
MCP_SERVER_URL=http://localhost:8000
MCP_AUTH_SERVER_URL=http://localhost:8000/auth
```

## Development workflow

### Step 1: Basic server

1. Create minimal FastMCP server
2. Add public tool and resource
3. Test with MCP Inspector

### Step 2: Add authentication

1. Implement demo auth provider
2. Add authorization endpoints
3. Test auth flow manually

### Step 3: Protect resources

1. Add bearer token middleware
2. Create protected endpoints
3. Test with authenticated requests

### Step 4: Polish and document

1. Add comprehensive logging
2. Write detailed documentation
3. Create example clients

## Success criteria

1. **Functional requirements**
   - Complete OAuth 2.1 authorization flow
   - Dynamic client registration support
   - Token refresh mechanism
   - Protected and public resources

2. **Educational requirements**
   - Clear, well-documented code
   - Progressive complexity
   - Helpful error messages
   - Complete example scenarios

3. **Technical requirements**
   - MCP protocol compliance
   - OAuth 2.1 standards compliance
   - Proper error handling
   - Comprehensive testing

## Next steps

1. Begin with Phase 1: Foundation setup
2. Implement core auth infrastructure
3. Add MCP server features
4. Create client examples
5. Document and test thoroughly

This plan provides a clear roadmap for building an educational MCP server with authentication that developers can learn from and adapt to their needs.