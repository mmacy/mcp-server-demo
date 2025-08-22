# MCP server demo with OAuth 2.1 authentication

A reference implementation demonstrating secure MCP (Model Context Protocol) servers with OAuth 2.1 authentication. This project showcases a complete two-service architecture that physically separates authentication concerns from resource serving, following OAuth 2.1 best practices.

This project implements a secure MCP server architecture with three components:

1. **Resource Server (RS)** - The MCP server that provides tools and resources
2. **Authorization Server (AS)** - The OAuth 2.1 server that handles authentication
3. **Client** - Example client demonstrating the complete three-party OAuth flow

The implementation serves as both a working example and the reference solution for a multi-part developer tutorial on building secure MCP servers.

## Architecture

```text
┌─────────────┐     OAuth 2.1       ┌────────────────────┐
│   Client    │◄───────────────────►│ Authorization      │
│             │                     │ Server (AS)        │
└─────┬───────┘                     │ - Login UI         │
      │                             │ - Token issuance   │
      │ MCP over HTTP               │ - Token validation │
      │ (with Bearer tokens)        └──────────┬─────────┘
      │                                        │
      ▼                                        │ HTTP
┌─────────────┐                                │ /introspect
│  Resource   │◄───────────────────────────────┘
│  Server     │     Token verification
│  (RS)       │
│ - MCP tools │
└─────────────┘
```

## Features

- **OAuth 2.1 compliant** - Full implementation of Authorization Code flow with PKCE
- **Physical service separation** - RS and AS are separate services communicating only via HTTP
- **Layered architecture** - Clean separation between web and logic layers
- **Progressive complexity** - Tutorial-oriented structure showing evolution from simple to structured
- **Security best practices** - Token validation, PKCE verification, secure defaults
- **FastMCP integration** - Built with the MCP Python SDK's FastMCP convenience wrapper

## Prerequisites

- Python 3.12 or higher
- [uv](https://docs.astral.sh/uv/) package manager

## Installation

1. Clone the repository:

```bash
git clone https://github.com/mmacy/mcp-server-demo.git
cd mcp-server-demo
```

2. Install dependencies:

```bash
uv sync
```

## Quick start

### Run the complete system

1. **Start the Authorization Server** (Terminal 1):

```bash
uv run src/authorization_server/server.py
```

The AS will run on `http://localhost:9000`. Verify it's running:

```bash
curl http://localhost:9000/.well-known/oauth-authorization-server
```

2. **Start the Resource Server** (Terminal 2):

```bash
uv run src/resource_server/server.py
```

The RS will run on `http://localhost:8000` with MCP endpoint at `/mcp`.

3. **Run the client** (Terminal 3):

```bash
uv run src/client.py
```

The client will:
- Discover OAuth metadata from both servers
- Dynamically register with the Authorization Server
- Open your browser for authentication
- Exchange authorization code for tokens
- Call both public and protected MCP tools

### Test with MCP Inspector

To test the Resource Server without authentication:

```bash
uv run mcp dev src/resource_server/server.py
```

This launches the MCP Inspector where you can interact with public tools.

## Configuration

### Resource Server settings

The RS can be configured via environment variables:

- `RS_SERVER_NAME` - Server name (default: "mcp-demo-resource-server")
- `RS_AUTH_ENABLED` - Enable authentication (default: true)
- `RS_AUTH_SERVER_URL` - Authorization Server URL (default: "http://localhost:9000")
- `RS_REQUIRE_AUTH_FOR_TOOLS` - Comma-separated list of protected tools (default: "server_time")
- `RS_LOG_LEVEL` - Logging level (default: "INFO")

### Authorization Server settings

The AS can be configured via environment variables:

- `AS_SERVER_PORT` - Server port (default: 9000)
- `AS_ISSUER` - Issuer URL (default: "http://localhost:9000")
- `AS_DEMO_USERNAME` - Demo username (default: "demo_user")
- `AS_DEMO_PASSWORD` - Demo password (default: "demo_password")
- `AS_TOKEN_LIFETIME` - Token lifetime in seconds (default: 3600)

## Available MCP tools

### Public tools

- **greet** - Generate a friendly greeting (no authentication required)
  - Parameters: `name` (string), `punctuation` (optional string)

### Protected tools

- **server_time** - Get current server time (requires authentication)
  - Returns: Current time, timezone, timestamp, and formatted time

## Tutorial structure

This project follows a 6-part tutorial progression:

### Part 1: Basic resource server
- Single-file FastMCP server with public tools
- Foundation for MCP server development

### Part 2: Authorization server foundation
- Separate AS with two-file structure (web + logic layers)
- OAuth 2.1 metadata endpoints

### Part 3: Complete AS implementation
- Full OAuth flow with PKCE
- Login UI and token issuance

### Part 4: Protect RS and refactor
- Add token verification to RS
- Refactor to layered structure
- Service-to-service communication

### Part 5: Client implementation
- Complete three-party OAuth flow
- Streamable HTTP transport with authentication

### Part 6: Enhanced patterns (not yet implemented)
- Advanced features
- Database persistence, token scopes, etc.

## Project structure

```txt
mcp-server-demo/
├── src/
│   ├── authorization_server/
│   │   ├── server.py         # AS web layer: routes and server setup
│   │   └── auth_provider.py  # AS logic layer: OAuth implementation
│   ├── resource_server/
│   │   ├── server.py         # RS app layer: server setup and auth
│   │   ├── settings.py       # RS configuration
│   │   └── tools.py          # RS content layer: MCP tool definitions
│   └── client.py             # Example client for three-party flow
├── pyproject.toml
├── README.md
├── CLAUDE.md                 # Development guidelines
└── PLAN.md                   # Tutorial implementation plan
```

## Development

### Running tests

```bash
uv run pytest tests/ -v
```

### Code style

The project follows:

- Google Python Style Guide with 120-character line length
- Type hints for all functions
- Extensive tutorial-oriented comments
- Clean separation of concerns

### Working with the code

Each Python file includes:

- Tutorial context in the module docstring
- SERVICE BOUNDARY comments at integration points
- TUTORIAL notes explaining key concepts
- Clear separation between layers and services

## Security considerations

This is a **demo implementation** for educational purposes:

- Uses in-memory storage (not persistent)
- Demo credentials are hardcoded
- Simplified error handling
- Not production-ready

For production use, consider:

- Persistent storage (database)
- Proper user authentication system
- Rate limiting and abuse prevention
- TLS/HTTPS for all communication
- Comprehensive error handling
- Token rotation and refresh

## Troubleshooting

### Common issues

1. **Port already in use**: The AS uses port 9000 and RS uses port 8000. Ensure these ports are available.
2. **Authentication fails**: Check that both servers are running and the RS has `RS_AUTH_ENABLED=true`.
3. **Browser doesn't open**: The client will print the authorization URL if the browser fails to open automatically.
4. **Token expires**: Default token lifetime is 1 hour. Restart the client to get a new token.

## License

CC0 1.0 Universal - See LICENSE file for details.

## Contributing

This is a reference implementation for a tutorial. Contributions should maintain:

- Clear teaching focus
- Progressive complexity
- Extensive documentation
- Service separation principles

## Resources

- [MCP Specification](https://modelcontextprotocol.io/specification/2025-06-18)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [OAuth 2.1 Specification](https://datatracker.ietf.org/doc/draft-ietf-oauth-v2-1/)
