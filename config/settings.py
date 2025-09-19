"""
Configuration settings for the Discord bot.
This module handles all configuration loading and environment variables.
"""

import os
import logging
from dotenv import load_dotenv
from typing import Optional

# Load environment variables from .env file
load_dotenv()

class BotConfig:
    """Configuration class for the Discord bot."""
    
    # Bot settings
    TOKEN: Optional[str] = os.getenv('DISCORD_TOKEN')
    COMMAND_PREFIX: str = os.getenv('COMMAND_PREFIX', '!')
    
    # Logging settings
    LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE: str = os.getenv('LOG_FILE', 'logs/discord.log')
    
    # Bot behavior settings
    DELETE_COMMANDS: bool = os.getenv('DELETE_COMMANDS', 'False').lower() == 'true'
    WELCOME_NEW_MEMBERS: bool = os.getenv('WELCOME_NEW_MEMBERS', 'True').lower() == 'true'
    
    # Moderation settings
    FILTERED_WORDS: list = ['yle']  # You can move this to environment variables too
    
    @classmethod
    def validate_config(cls) -> bool:
        """Validate that all required configuration is present."""
        if not cls.TOKEN:
            raise ValueError("DISCORD_TOKEN environment variable is required!")
        return True

def setup_logging() -> logging.Handler:
    """Setup logging configuration for the bot."""
    # Ensure logs directory exists
    os.makedirs(os.path.dirname(BotConfig.LOG_FILE), exist_ok=True)
    
    # Create file handler
    handler = logging.FileHandler(
        filename=BotConfig.LOG_FILE, 
        encoding='UTF-8', 
        mode='w'
    )
    
    # Set log level
    log_level = getattr(logging, BotConfig.LOG_LEVEL.upper(), logging.INFO)
    handler.setLevel(log_level)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    
    return handler