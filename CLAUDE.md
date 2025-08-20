# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## MCP Server Demo

This is a Python-based Model Context Protocol (MCP) server implementation with authentication, session management, and protected resources.

The audience of this project are experienced MCP server developers also experienced in Python, but new to authorization in MCP servers.

### Important reference

The MCP Python SDK is available locally at `../mcp-python-sdk/` and its source code in `../mcp-python-sdk/src/mcp` should be used as the authoritative reference during implementation. Always check the SDK source code for correct API usage, not just the documentation.

The Authorization section of the MCP protocol specification is available in `mcp-specification-202506-18-authorization.md`. You MAY refer to this specification if you have questions about the standards or need pointers to other sources of information linked-to from the spec.

## Core development rules

1. Package management: You MUST use `uv` rather than `pip` in all contexts

2. Code quality

   - Type hints required for all code
   - All public members MUST have Google Python Style Guide-compliant docstrings
   - Functions must be focused and small
   - Line length: 120 chars maximum

3. Documentation quality: see "Docstring best practices for Python documentation" below

## Running the server

```bash
# Run the MCP server directly
uv run server.py

# Run with MCP Inspector (for testing)
uv run mcp dev server.py
```

## Architecture overview

This project implements an MCP server with authentication following these patterns:

1. **Server implementation**:

   - `FastMCP` (from `mcp.server.fastmcp`): High-level API for quick development, recommended for most use cases

2. **Server reatures**:

   - Token-based authentication
   - Secure credential handling
   - Session management
   - Basic access control for protected resources

### Implementation patterns from SDK

When implementing features, you MUST refer to the source code in `../mcp-python-sdk/src/mcp/` as authoritative.

You MAY also reference SDK examples in `../mcp-python-sdk/examples/` as a secondary source of guidance.

You SHOULD use both `../mcp-python-sdk/src/mcp/` and `../mcp-python-sdk/examples/` to help ensure a robust solution.

### Server configuration

FastMCP uses Pydantic BaseSettings for configuration with the environment variable prefix FASTMCP_ and nested model support via FASTMCP__ (double underscore) as the delimiter. A local .env file is loaded automatically.

Example: Basic local development

```ini
FASTMCP_DEBUG=true
FASTMCP_LOG_LEVEL=DEBUG
FASTMCP_HOST=127.0.0.1
FASTMCP_PORT=8000

# SSE and Streamable HTTP paths
FASTMCP_MOUNT_PATH=/
FASTMCP_SSE_PATH=/sse
FASTMCP_MESSAGE_PATH=/messages/
FASTMCP_STREAMABLE_HTTP_PATH=/mcp

# Streamable HTTP behavior
FASTMCP_JSON_RESPONSE=false
FASTMCP_STATELESS_HTTP=false
```

## Docstring best practices for Python documentation

The following guidance ensures docstrings are genuinely helpful for new users by providing navigation, context, and accurate examples.

### Structure and formatting

- Follow the Google Python Style Guide for docstrings.
- Format docstrings in Markdown compatible with documentation generators like `mkdocs-material` with the `mkdocstrings` plugin.
- Always surround headings with blank lines.
- Always surround lists with blank lines.
- Always surround fenced code blocks with blank lines.
- Use sentence case for all headings and heading-like text.

### Content requirements

- **Usage patterns**: Explain how users typically interact with a class or function. Explicitly state the common use cases or intended sequence of calls with phrases like "This function is typically called by..." or "You can get an instance of this class through...".

- **Cross-references**: Use extensive cross-references to related components to help users navigate the codebase.

  - Format: [`displayed_text`][module.path.to.Member]
  - Include backticks around the displayed text.
  - Link to types, related functions or methods, and alternative approaches.

- **Parameter descriptions**:

  - Document all valid values for parameters that accept enums or literal values.
  - Explain what each parameter does and in which context to use it.
  - Cross-reference parameter types when it aids understanding.

- **Real-world examples**:

  - Show actual usage patterns from the project, not just theoretical or abstract code snippets.
  - Include necessary imports and use complete module paths.
  - Verify all examples against the current source code for accuracy.
  - If applicable, show multiple approaches (e.g., using a high-level API versus lower-level components).
  - Add comments to the code to explain what's happening.
  - Examples should be concise and only as complex as needed to demonstrate real-world usage clearly.

- **Context and purpose**:

  - Explain not just *what* a component does, but *why* and *when* a developer should use it.
  - Include notes about important considerations, such as performance implications, side effects, or thread safety.
  - Mention alternative approaches or related components where applicable.

### Verification

- All code examples MUST be 100% accurate to the implementation in the source code.
- Verify imports, class names, and function or method signatures against the source code.
- You MUST NOT rely on existing documentation as authoritative; you MUST check the source code.
