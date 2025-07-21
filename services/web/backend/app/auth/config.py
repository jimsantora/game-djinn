"""Authentication configuration."""

import os
from typing import Optional
from pydantic import BaseModel


class AuthConfig(BaseModel):
    """Authentication configuration from environment variables."""
    
    # Admin credentials (optional)
    admin_email: Optional[str] = None
    admin_password: Optional[str] = None
    
    # JWT configuration
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    
    # MCP API key
    mcp_api_key: str
    
    @property
    def auth_enabled(self) -> bool:
        """Check if authentication is enabled."""
        return bool(self.admin_email and self.admin_password)
    
    @classmethod
    def from_env(cls) -> "AuthConfig":
        """Load configuration from environment variables."""
        return cls(
            admin_email=os.getenv("ADMIN_EMAIL"),
            admin_password=os.getenv("ADMIN_PASSWORD"),
            secret_key=os.getenv("SECRET_KEY", "dev-secret-key-change-in-production"),
            mcp_api_key=os.getenv("MCP_API_KEY", "dev-mcp-key"),
            access_token_expire_minutes=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")),
            refresh_token_expire_days=int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))
        )


# Global auth configuration instance
auth_config = AuthConfig.from_env()