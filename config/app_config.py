# config/app_config.py
import os
from typing import NamedTuple, Optional
from dotenv import load_dotenv

class ConfigError(Exception):
    """Raised when configuration is invalid"""
    pass

class AppConfig(NamedTuple):
    """Application configuration settings with validation"""
    discord_token: str
    log_channel_id: int
    deals_channel_id: int
    itad_api_key: str
    debug_api_responses: bool = False
    
    def validate(self) -> None:
        """Validate configuration values"""
        if not self.discord_token:
            raise ConfigError("DISCORD_TOKEN is required")
        if self.log_channel_id <= 0:
            raise ConfigError("LOG_CHANNEL_ID must be a valid positive integer")
        # ITAD_API_KEY is optional but should be warned about if missing
        
    @property
    def is_valid(self) -> bool:
        """Check if configuration is valid without raising exceptions"""
        try:
            self.validate()
            return True
        except ConfigError:
            return False

def load_config() -> AppConfig:
    """Load configuration from environment variables with validation"""
    load_dotenv()
    
    discord_token: str = os.getenv("DISCORD_TOKEN", "")
    
    # Parse channel IDs with error handling
    try:
        log_channel_id: int = int(os.getenv("LOG_CHANNEL_ID", "0"))
    except ValueError:
        raise ConfigError("LOG_CHANNEL_ID must be a valid integer")
        
    try:
        deals_channel_id: int = int(os.getenv("DEALS_CHANNEL_ID", str(log_channel_id)))
    except ValueError:
        raise ConfigError("DEALS_CHANNEL_ID must be a valid integer")
    
    itad_api_key: str = os.getenv("ITAD_API_KEY", "")
    debug_api_responses: bool = os.getenv("DEBUG_API_RESPONSES", "false").lower() == "true"
    
    return AppConfig(
        discord_token=discord_token,
        log_channel_id=log_channel_id,
        deals_channel_id=deals_channel_id,
        itad_api_key=itad_api_key,
        debug_api_responses=debug_api_responses
    )