# config/logging_config.py
import logging
import os
from typing import Optional

# Write logs into ./logs/discord.log 
ROOT_DIR = os.path.dirname(os.path.dirname(__file__))  
LOG_DIR = os.path.join(ROOT_DIR, "logs")

def get_log_directory() -> str:
    """Get the log directory path, creating it if necessary"""
    os.makedirs(LOG_DIR, exist_ok=True)
    return LOG_DIR

def setup_logging(level: int = logging.INFO, force_reconfigure: bool = True) -> logging.Logger:
    """
    Setup centralized logging configuration for the GameDealer bot.
    
    Args:
        level: Logging level (default: INFO)
        force_reconfigure: Whether to force reconfiguration of logging (default: True)
        
    Returns:
        Configured logger instance
    """
    # Clear any existing handlers to prevent conflicts if force_reconfigure is True
    if force_reconfigure:
        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)
    
    # Ensure log directory exists
    log_dir = get_log_directory()
    
    # Configure logging with proper handlers
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(os.path.join(log_dir, 'discord.log'), encoding='utf-8'),
            logging.StreamHandler()
        ],
        force=force_reconfigure
    )
    
    # Return a logger for the calling module
    return logging.getLogger('GameDealer')

def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Get a logger instance. Call setup_logging() first.
    
    Args:
        name: Logger name (default: calling module name)
        
    Returns:
        Logger instance
    """
    return logging.getLogger(name or 'GameDealer')
