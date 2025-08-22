# MCP server demo - implementation plan

## Project purpose

This project serves as the **completed reference implementation** for a multi-part developer tutorial on building secure MCP servers. Its architecture physically separates the **Resource Server (RS)** from the **Authorization Server (AS)** and organizes each service internally for clarity and scalability.

## Tutorial design principles

### Developer journey

1.  **Start simple** - Build a working, single-file Resource Server (which is also the MCP server).
2.  **Build the second service** - Create the Authorization Server with a clean two-file structure.
3.  **Connect and protect** - Integrate the two services to secure the RS.
4.  **Refactor for clarity** - Refactor the RS to mirror the clean structure of the AS.
5.  **Test continuously** - Each part ends with a testable, working system.

### Code organization for learning

-   **Clear service boundaries** - The RS and AS live in separate, self-contained directories.
-   **Separation of concerns** - Each service separates its web layer from its logic layer.
-   **Extensive comments** - Explain the "why," not just the "what."
-   **Checkpoint branches** - Git tags for each tutorial completion point.

## Tutorial parts with milestones

### Part 1: Basic resource server

**Learning objective**: Create a standalone **Resource Server (RS)**  that's the **MCP server** and the foundation of the project.

**What developers will build**:

-   A `resource_server/` directory containing a single `server.py` file.
-   This file will contain a basic, runnable `FastMCP` application with one tool.

**Verification checkpoint**:

-   Run the RS with `uv run mcp dev resource_server/server.py`.
-   Test the tool in the MCP Inspector.

**Files created**:

-   `resource_server/server.py`

### Part 2: Standalone authorization server foundation

**Learning objective**: Build a separate, standalone **Authorization Server (AS)** with a clean two-file structure.

**What developers will build**:

-   An `authorization_server/` directory.
-   `authorization_server/server.py`: The web layer, responsible for setting up the server and defining HTTP routes.
-   `authorization_server/auth_provider.py`: The logic layer, responsible for the core OAuth logic (initially a stub).

**Verification checkpoint**:

-   Run the AS with `uv run authorization_server/server.py`.
-   Access `http://localhost:9000/.well-known/oauth-authorization-server`.

### Part 3: Implement AS authentication flow

**Learning objective**: Complete the core logic of the **Authorization Server (AS)** to handle the full OAuth flow.

**What developers will build**:

-   Add the full implementation for token and code generation to `auth_provider.py`.
-   Wire up the logic to the routes in `server.py` for the login form, authorization, and token endpoints.

**Verification checkpoint**:

-   Run the AS.
-   Manually perform the auth flow in a browser to obtain an access token.

### Part 4: Protect the resource server and refactor

**Learning objective**: Secure the **RS** by connecting it to the **AS**, and refactor the RS for better organization.

**What developers will build**:

-   **In `resource_server/server.py`**: Add a `TokenVerifier` class and middleware to protect the server.
-   **Create `resource_server/tools.py`**: Move the existing tool here and add a new protected tool.
-   **Create `resource_server/settings.py`**: Move the `ResourceServerSettings` into its own module so `server.py` and `tools.py` can both acces it.
-   **Update `resource_server/server.py`**: Import and register the tools from `tools.py`.

**Verification checkpoint**:

-   Run both the AS and RS in separate terminals.
-   Confirm public tools on the RS work without a token; protected tools return a 401.

### Part 5: Add client examples

**Learning objective**: Build a client that orchestrates the full three-party authentication flow.

**What developers will build**:

-   A `client.py` that connects to the RS, triggers the login flow on the AS, and uses the obtained token to access protected tools on the RS.

**Verification checkpoint**:

-   With both servers running, execute `uv run client.py`.
-   The client should successfully authenticate and call both public and protected tools.

### Part 6: Enhanced patterns

**Learning objective**: Enhance both services with more robust features that demonstrate advanced concepts.

**What developers will enhance**:

-   **AS**: Modify `auth_provider.py` to use a database for persistent token storage.
-   **RS**: Modify `server.py` to check for specific token scopes.
-   **Both**: Add configuration files to manage settings.

## File structure for tutorial clarity

```

mcp-server-demo/
├── authorization_server/
│   ├── __init__.py
│   ├── server.py         # AS web layer: routes and server setup
│   └── auth_provider.py  # AS logic layer: core OAuth implementation
├── resource_server/
│   ├── __init__.py
│   ├── server.py         # RS app layer: server setup and auth protection
│   └── tools.py          # RS content layer: MCP tool definitions
├── client.py             # Example client to test the full flow
├── tests/
│   ├── test_resource_server.py
│   └── test_auth_server.py
├── .env.example
├── pyproject.toml
└── README.md
```

## Git strategy for tutorial

### Branch/tag structure

```
main                  # Complete implementation
├── tutorial/part-1   # Tag: Basic RS
├── tutorial/part-2   # Tag: AS Foundation
├── tutorial/part-3   # Tag: AS Auth Flow
├── tutorial/part-4   # Tag: Protected & Refactored RS
├── tutorial/part-5   # Tag: Client Example
└── tutorial/part-6   # Tag: Enhanced Patterns
```

### Commit message pattern

```text
Part X (Service): [Feature] - [What it teaches]

Example:
Part 2 (AS): Create web and logic layers - Teaches separation of concerns
Part 4 (RS): Add token verifier - Teaches service-to-service validation
```

## Implementation guidelines

### Code style for learning

  - **Separation of concerns**: Enforce component split from the start.
  - **Explicit over implicit**: Show the `httpx` call from the RS's `TokenVerifier` to the AS's endpoints.
  - **Clear imports**: `from . import tools` and `from . import auth_provider` make dependencies obvious.

### Progressive complexity

1.  **Part 1**: A single, runnable service in one file.
2.  **Part 2**: A second service built with a two-file structure.
3.  **Part 3**: Flesh out the logic in the AS.
4.  **Part 4**: Integrate the two services and refactor the first service to match the cleaner structure.
5.  **Part 5-6**: Add the client and enhance both services with production features.

## Success metrics

1.  A developer understands and can replicate the clean, two-file structure for both services.
2.  The relationship and clear boundaries between a service's web layer and logic layer are understood.
3.  The final project is well-organized, spec-compliant, and easy to extend.

## Development workflow

1.  Build the final, complete two-service implementation.
2.  Work backwards to create the state for each tutorial part, ensuring the step-by-step creation and refactoring process is logical.
3.  Tag each part and test the progression.
