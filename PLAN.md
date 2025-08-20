# MCP server demo - implementation plan

## Project purpose

This project serves as the **completed reference implementation** for a multi-part developer tutorial on building MCP servers with authentication. Each phase below corresponds to a tutorial part, with every step producing a working, testable server that developers can verify against this reference.

## Tutorial design principles

### Developer journey

1. **Start simple** - Begin with a working MCP server without auth
2. **Add incrementally** - Each tutorial part adds one major concept
3. **Test continuously** - Every phase ends with a testable milestone
4. **Learn by doing** - Code first, theory follows from practice
5. **Compare and verify** - Developers can check their work against this repo

### Code organization for learning

- **Clear file boundaries** - Each module has a single, clear purpose
- **Progressive disclosure** - Advanced features in separate files
- **Extensive comments** - Explain the "why" not just the "what"
- **Checkpoint branches** - Git tags for each tutorial completion point

## Tutorial parts with milestones

### Part 1: Basic MCP server (no auth)

**Learning objective**: Understand MCP server basics and FastMCP

**What developers will build**:

```python
# server.py - Complete working server
from mcp.server.fastmcp import FastMCP

server = FastMCP("demo-server")

@server.tool()
async def get_time():
    """Get current server time."""
    from datetime import datetime
    return datetime.now().isoformat()

@server.resource("text/plain")
async def readme():
    """Get server information."""
    return "MCP Demo Server - Part 1 Complete"
```

**Verification checkpoint**:

- Run with `uv run mcp dev server.py`
- Test tool execution in MCP Inspector
- Confirm resource listing works

**Files created**:

- `server.py` - Main server file
- `pyproject.toml` - Dependencies
- `.env.example` - Environment template
- `README.md` - Setup instructions

### Part 2: Add authorization server foundation

**Learning objective**: Understand OAuth 2.1 server role and metadata

**What developers will build**:

- Add `auth/` directory structure
- Implement metadata endpoints
- Create demo provider skeleton
- Add auth server routes

**New files**:

```
auth/
├── __init__.py
├── provider.py        # OAuth provider interface
├── demo_provider.py   # Simple implementation
└── metadata.py        # Server metadata endpoints
```

**Verification checkpoint**:

- Access `/.well-known/oauth-authorization-server`
- Access `/.well-known/oauth-protected-resource`
- Server still works with existing tools

### Part 3: Implement authentication flow

**Learning objective**: Understand OAuth authorization code flow

**What developers will build**:

- Login form endpoint
- Authorization endpoint
- Token exchange endpoint
- State management

**Enhanced files**:

- `auth/demo_provider.py` - Full auth flow
- `auth/templates.py` - Login form HTML
- `auth/tokens.py` - Token generation

**Verification checkpoint**:

- Complete manual auth flow in browser
- Obtain access token via curl
- Verify token structure

### Part 4: Protect MCP resources

**Learning objective**: Connect OAuth tokens to MCP access control

**What developers will build**:

- Bearer token middleware
- Protected tool decorators
- Auth context injection
- WWW-Authenticate headers

**New files**:

```
auth/
├── middleware.py      # Bearer token validation
├── context.py         # Auth context for tools
tools/
├── __init__.py
├── public.py         # Public tools (moved from server.py)
└── protected.py      # New protected tools
```

**Verification checkpoint**:

- Public tools work without auth
- Protected tools require valid token
- 401 responses include proper headers

### Part 5: Add client examples

**Learning objective**: Understand client-side auth flow

**What developers will build**:

- Python client with auth
- Token refresh logic
- Error handling

**New files**:

```
examples/
├── client.py         # Full auth client
├── test_auth.py      # Auth flow tests
└── demo_session.py   # Interactive demo
```

**Verification checkpoint**:

- Client obtains token automatically
- Client accesses protected resources
- Token refresh works

### Part 6: Production patterns

**Learning objective**: Make it production-ready

**What developers will enhance**:

- Persistent token storage
- Scope-based access control
- Revocation support
- Security headers
- Rate limiting

**Enhanced files**:

- `auth/storage.py` - Token persistence
- `auth/scopes.py` - Scope validation
- `config.py` - Production settings

**Final verification**:

- All OAuth 2.1 flows work
- Security best practices applied
- Ready for deployment

## File structure for tutorial clarity

```
mcp-server-demo/
├── server.py                 # Main entry - grows with each part
├── config.py                 # Settings - added in Part 2
├── auth/                     # Added in Part 2
│   ├── __init__.py
│   ├── provider.py          # Abstract base - Part 2
│   ├── demo_provider.py     # Implementation - Part 2-3
│   ├── metadata.py          # Endpoints - Part 2
│   ├── tokens.py            # Management - Part 3
│   ├── middleware.py        # Protection - Part 4
│   ├── context.py           # Auth context - Part 4
│   ├── storage.py           # Persistence - Part 6
│   └── scopes.py            # Access control - Part 6
├── tools/                    # Refactored in Part 4
│   ├── __init__.py
│   ├── public.py            # No auth required
│   └── protected.py         # Auth required
├── resources/                # Refactored in Part 4
│   ├── __init__.py
│   ├── public.py
│   └── protected.py
├── examples/                 # Added in Part 5
│   ├── client.py
│   ├── test_auth.py
│   └── demo_session.py
├── tests/                    # Added progressively
│   ├── test_part1.py        # Basic server tests
│   ├── test_part2.py        # Metadata tests
│   ├── test_part3.py        # Auth flow tests
│   ├── test_part4.py        # Protection tests
│   ├── test_part5.py        # Client tests
│   └── test_part6.py        # Production tests
├── .env.example              # Grows with each part
├── pyproject.toml            # Dependencies added per part
└── README.md                 # Tutorial checkpoint guide
```

## Git strategy for tutorial

### Branch/tag structure

```
main                  # Complete implementation
├── tutorial/part-1   # Tag: Basic server
├── tutorial/part-2   # Tag: Auth foundation
├── tutorial/part-3   # Tag: Auth flow
├── tutorial/part-4   # Tag: Protected resources
├── tutorial/part-5   # Tag: Client examples
└── tutorial/part-6   # Tag: Production ready
```

### Commit message pattern

```
Part X: [Feature] - [What it teaches]

Example:
Part 2: Add OAuth metadata endpoints - Teaches server discovery
Part 4: Implement bearer token validation - Teaches resource protection
```

## Documentation requirements

### In-code documentation

Each file must include:

1. **File header** explaining its role in the tutorial
2. **Function docstrings** with learning notes
3. **Inline comments** for non-obvious logic
4. **TODO markers** for tutorial exercises

Example:

```python
"""
Part 4: Bearer token middleware

This module validates OAuth 2.0 bearer tokens for protected resources.
Tutorial readers will learn:
- How to extract tokens from headers
- When to return 401 vs 403
- How to inject auth context

TODO (Exercise 4.1): Add token expiration check
TODO (Exercise 4.2): Implement scope validation
"""
```

### README sections

Each part needs:

1. **What you'll learn** - Clear learning objectives
2. **Prerequisites** - What parts must be complete
3. **New concepts** - Technical concepts introduced
4. **Step-by-step** - Detailed implementation steps
5. **Testing** - How to verify it works
6. **Troubleshooting** - Common issues and fixes
7. **Next steps** - Preview of next part

## Implementation guidelines

### Code style for learning

1. **Explicit over implicit** - No magic, show all steps
2. **Verbose variable names** - `authorization_code` not `auth_code`
3. **Group related code** - Keep auth stuff in auth/
4. **Avoid over-abstraction** - Some repetition is OK for clarity
5. **Error messages that teach** - Explain what went wrong and why

### Progressive complexity

Start simple, add complexity only when needed:

1. **Part 1-3**: Hardcoded values OK (demo only)
2. **Part 4-5**: Add configuration options
3. **Part 6**: Production patterns

### Testing philosophy

Each part has tests that:

1. **Verify the happy path** - What should work
2. **Test error cases** - What should fail
3. **Demonstrate usage** - Tests as documentation
4. **Build confidence** - Developers know it works

## Success metrics

This reference implementation succeeds when:

1. **Developers can follow along** - Each part builds successfully
2. **Concepts are clear** - Auth flow makes sense
3. **Code is debuggable** - Easy to troubleshoot issues
4. **Production-ready** - Final result is usable
5. **Extensible** - Easy to add custom auth providers

## Development workflow

### Building the reference

1. **Start with Part 6** - Build complete implementation
2. **Work backwards** - Strip features for earlier parts
3. **Tag each part** - Create checkpoint tags
4. **Test progression** - Verify part-by-part build
5. **Document thoroughly** - Explain every decision

### Creating the tutorial

1. **Write as you build** - Document fresh insights
2. **Test with beginners** - Get feedback early
3. **Include diagrams** - Visual auth flow
4. **Provide exercises** - Let developers practice
5. **Offer solutions** - Complete code for checking

## Next steps

1. Build complete implementation (Part 6)
2. Create git tags for each part
3. Write tutorial Part 1
4. Test with target audience
5. Iterate based on feedback

This plan ensures the code serves its primary purpose: teaching developers how to add authentication to MCP servers through hands-on, incremental learning.