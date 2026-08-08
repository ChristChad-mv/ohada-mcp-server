"""Configuration settings for the OHADA MCP server."""

from pathlib import Path
from typing import Annotated

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


class Settings(BaseSettings):
    """Server and environment configuration."""

    HOST: str = "127.0.0.1"
    PORT: int = 8080
    MCP_PATH: str = "/mcp"
    OHADA_DB_PATH: Path = Path("ohada_corpus.sqlite")

    # Production transport protection. Values can be supplied as JSON arrays or
    # comma-separated environment variables.
    ENABLE_DNS_REBINDING_PROTECTION: bool = True
    ALLOWED_HOSTS: Annotated[list[str], NoDecode] = Field(
        default_factory=lambda: ["localhost:*", "127.0.0.1:*", "[::1]:*"]
    )
    ALLOWED_ORIGINS: Annotated[list[str], NoDecode] = Field(
        default_factory=lambda: [
            "http://localhost:*",
            "http://127.0.0.1:*",
            "http://[::1]:*",
        ]
    )
    STATELESS_HTTP: bool = True
    JSON_RESPONSE: bool = True
    MAX_REQUEST_BODY_SIZE: int = 65_536

    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_REQUESTS: int = 120
    RATE_LIMIT_WINDOW_SECONDS: int = 60
    RATE_LIMIT_MAX_CLIENTS: int = 10_000

    MAX_SEARCH_RESULTS: int = 10
    MAX_QUERY_LENGTH: int = 1_000
    SEARCH_SNIPPET_LENGTH: int = 600

    @field_validator("MCP_PATH")
    @classmethod
    def validate_mcp_path(cls, value: str) -> str:
        value = value.strip()
        if not value.startswith("/") or value == "/":
            raise ValueError("MCP_PATH must be an absolute non-root path")
        return value.rstrip("/")

    @field_validator("ALLOWED_HOSTS", "ALLOWED_ORIGINS", mode="before")
    @classmethod
    def parse_list_setting(cls, value):
        if isinstance(value, str):
            value = value.strip()
            if value.startswith("["):
                import json

                return json.loads(value)
            return [item.strip() for item in value.split(",") if item.strip()]
        return value

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=True,
    )


settings = Settings()
