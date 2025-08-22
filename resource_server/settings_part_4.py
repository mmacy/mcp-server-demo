"""
Part 4 (Resource Server): Configuration settings

This module defines the configuration for the Resource Server, extracted from server.py
to avoid circular imports between server.py and tools.py.

Tutorial context:

- Added in Part 4
- Service: RS (Resource Server)
- Layer: Configuration
- Teaches: Configuration management, avoiding circular imports
- Prerequisites: Understanding of pydantic-settings

Key learning points:

- Settings are centralized and environment-aware
- Using a separate settings module prevents circular imports
- Configuration can be overridden via environment variables
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class ResourceServerSettings(BaseSettings):
    """Configuration for the Resource Server (MCP server)."""

    model_config = SettingsConfigDict(env_prefix="RS_", env_file=".env", extra="ignore")

    # Tutorial Part 1: Basic server
    server_name: str = "mcp-demo-resource-server"

    # Tutorial Part 4: Auth integration
    auth_enabled: bool = False
    # Base URL for the Authorization Server (e.g., http://localhost:9000)
    auth_server_url: str = "http://localhost:9000"
    # List of tool names that require auth. If empty and auth_enabled=True, ALL require auth.
    require_auth_for_tools: list[str] = ["server_time"]

    # Application-level settings
    log_level: str = "INFO"
