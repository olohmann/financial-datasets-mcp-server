import os
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv

@dataclass
class Config:
    """Configuration settings for the MCP server."""
    api_key: Optional[str] = None
    base_url: str = "https://api.financialdatasets.ai"
    default_timeout: float = 30.0
    health_check_timeout: float = 5.0
    log_level: str = "INFO"
    transport_type: str = "stdio"
    host: str = "127.0.0.1"
    port: int = 8000
    cache_ttl_minutes: int = 10
    
    @classmethod
    def from_env(cls) -> "Config":
        """Create config from environment variables."""
        return cls(
            api_key=os.environ.get("FINANCIAL_DATASETS_API_KEY"),
            base_url=os.environ.get("FINANCIAL_DATASETS_API_BASE", cls.base_url),
            default_timeout=float(os.environ.get("API_TIMEOUT", cls.default_timeout)),
            health_check_timeout=float(os.environ.get("HEALTH_CHECK_TIMEOUT", cls.health_check_timeout)),
            log_level=os.environ.get("LOG_LEVEL", cls.log_level),
            transport_type=os.environ.get("MCP_TRANSPORT", cls.transport_type),
            host=os.environ.get("MCP_HOST", cls.host),
            port=int(os.environ.get("MCP_PORT", cls.port)),
            cache_ttl_minutes=int(os.environ.get("CACHE_TTL_MINUTES", cls.cache_ttl_minutes)),
        )

# Load environment variables first
load_dotenv()

config = Config.from_env()