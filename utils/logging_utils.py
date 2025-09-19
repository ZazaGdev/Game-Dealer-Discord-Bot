"""
Logging utilities for the Discord bot.
This module provides enhanced logging functionality and log management.
"""

import logging
import os
from datetime import datetime
from pathlib import Path
from config import BotConfig

def setup_custom_logger(name: str) -> logging.Logger:
    """
    Set up a custom logger with file and console handlers.
    
    Args:
        name (str): The name of the logger
    
    Returns:
        logging.Logger: Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, BotConfig.LOG_LEVEL.upper(), logging.INFO))
    
    # Prevent duplicate handlers
    if logger.handlers:
        return logger
    
    # Create logs directory if it doesn't exist
    log_dir = Path(BotConfig.LOG_FILE).parent
    log_dir.mkdir(exist_ok=True)
    
    # File handler
    file_handler = logging.FileHandler(
        filename=BotConfig.LOG_FILE,
        encoding='utf-8',
        mode='a'  # Append mode
    )
    
    # Console handler
    console_handler = logging.StreamHandler()
    
    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

def log_command_usage(user: str, command: str, guild: str = None):
    """
    Log command usage for analytics and debugging.
    
    Args:
        user (str): Username who used the command
        command (str): Command that was used
        guild (str): Guild where command was used (optional)
    """
    logger = logging.getLogger('command_usage')
    
    guild_info = f" in {guild}" if guild else ""
    logger.info(f"Command '{command}' used by {user}{guild_info}")

def log_moderation_action(action: str, user: str, moderator: str, reason: str = None):
    """
    Log moderation actions for audit purposes.
    
    Args:
        action (str): The moderation action taken
        user (str): User who was moderated
        moderator (str): Moderator who took the action
        reason (str): Reason for the action (optional)
    """
    logger = logging.getLogger('moderation')
    
    reason_info = f" - Reason: {reason}" if reason else ""
    logger.warning(f"Moderation: {action} applied to {user} by {moderator}{reason_info}")

def cleanup_old_logs(max_age_days: int = 30):
    """
    Clean up old log files to save disk space.
    
    Args:
        max_age_days (int): Maximum age of log files to keep (default: 30 days)
    """
    log_dir = Path(BotConfig.LOG_FILE).parent
    
    if not log_dir.exists():
        return
    
    current_time = datetime.now()
    
    for log_file in log_dir.glob("*.log*"):
        file_age = current_time - datetime.fromtimestamp(log_file.stat().st_mtime)
        
        if file_age.days > max_age_days:
            try:
                log_file.unlink()
                print(f"🗑️ Cleaned up old log file: {log_file.name}")
            except Exception as e:
                print(f"❌ Failed to delete log file {log_file.name}: {e}")