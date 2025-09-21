# config/app_config.py
import os
from typing import NamedTuple
from dotenv import load_dotenv

class AppConfig(NamedTuple):
    """Application configuration settings"""
    discord_token: str
    log_channel_id: int
    deals_channel_id: int
    itad_api_key: str
    debug_api_responses: bool = False

def load_config() -> AppConfig:
    """Load configuration from environment variables"""
    load_dotenv()
    
    discord_token = os.getenv("DISCORD_TOKEN", "")
    log_channel_id = int(os.getenv("LOG_CHANNEL_ID", "0"))
    deals_channel_id = int(os.getenv("DEALS_CHANNEL_ID", str(log_channel_id)))
    itad_api_key = os.getenv("ITAD_API_KEY", "")
    debug_api_responses = os.getenv("DEBUG_API_RESPONSES", "false").lower() == "true"
    
    return AppConfig(
        discord_token=discord_token,
        log_channel_id=log_channel_id,
        deals_channel_id=deals_channel_id,
        itad_api_key=itad_api_key,
        debug_api_responses=debug_api_responses
    )